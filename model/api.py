from fastapi import FastAPI, Body, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

import os

from model.db.data import User, Account, Transaction
from model.db.mongo import DBClient
from model.db.encryption import encrypt_password, generate_token, decrypt_token

app = FastAPI()

# Connect to the MongoDB database
username, password = os.environ['MONGO_INITDB_ROOT_USERNAME'], os.environ['MONGO_INITDB_ROOT_PASSWORD']
db_client = DBClient(host="mongo", port=27017, username=username, password=password)

# Allow all origins (adjust according to your security requirements)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JWT_ACCESS_TOKEN_EXPIRATION = 60 * 15 # 15 minutes
JWT_REFRESH_TOKEN_EXPIRATION = 60 * 60 * 3 # 3 hours

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/signup")
def signup(user: User):
    # Verify that the user does not already exist
    if not db_client.unique_email(user.email):
        raise HTTPException(status_code=409, detail="Email already exists")
    else :
        # Save the user
        authentication_hash = encrypt_password(user.authentication_hash, user.email)
        user.authentication_hash = authentication_hash
        inserted_id = db_client.save_user(user)
        return {"id": inserted_id}

@app.post("/login")
def login(user: User, response: Response):
    # Verify that the user exists
    authentication_hash = encrypt_password(user.authentication_hash, user.email)
    res = db_client.verify_user(authentication_hash)
    if res is None:
        if not db_client.unique_email(user.email):
            raise HTTPException(status_code=400, detail="Incorrect password")
        else:    
            raise HTTPException(status_code=400, detail="Incorrect email address")
    else:
        # Generate a short-lived access token and a long-lived refresh token
        access_token = generate_token(JWT_ACCESS_TOKEN_EXPIRATION, os.environ['JWT_SECRET'])
        refresh_token = generate_token(JWT_REFRESH_TOKEN_EXPIRATION, os.environ['JWT_SECRET'])

        # Update the user in the database
        db_client.update_user(res.id, access_token=access_token, refresh_token=refresh_token)

        # Set the access and refresh token as a cookie in the response
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

        return response
