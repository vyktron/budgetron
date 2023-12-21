from fastapi import FastAPI, Body, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import os

from model.db.data import User, Account, Transaction, Bank
from model.db.mongo import DBClient
from model.db.encryption import *
from model.extract import BankDataExtractor, WebsiteProvider

app = FastAPI()

#TODO Handle 401 errors messages and when Server is down

# Connect to the MongoDB database
username, password = os.environ['MONGO_INITDB_ROOT_USERNAME'], os.environ['MONGO_INITDB_ROOT_PASSWORD']
db_client = DBClient(host="mongo", port=27017, username=username, password=password)

# Allow all origins (adjust according to your security requirements)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], #TODO change this to the frontend url
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD", "OPTIONS"],
    allow_headers=["set-cookie", "content-type"],
)

JWT_ACCESS_TOKEN_EXPIRATION = 5*60 # 5 minutes
JWT_REFRESH_TOKEN_EXPIRATION = 60 * 60 # 1 hour

########## Authentication Endpoints ##########

@app.post("/signup")
def signup(user: User):
    # Verify that the user does not already exist
    if not (db_client.user_by_email(user.email) is None):
        raise HTTPException(status_code=409, detail="Email already exists")
    else :
        # Save the user
        authentication_hash = encrypt_password(user.authentication_hash, user.email)
        user.authentication_hash = authentication_hash
        inserted_id = db_client.save_user(user)
        return {"id": inserted_id}

@app.post("/login")
def login(user: User):
    # Verify that the user exists
    authentication_hash = encrypt_password(user.authentication_hash, user.email)
    res = db_client.verify_user(authentication_hash)
    if res is None:
        if not (db_client.user_by_email(user.email) is None):
            raise HTTPException(status_code=400, detail="Incorrect password")
        else:
            raise HTTPException(status_code=400, detail="Incorrect email address")
    else:
        # Generate a long-lived refresh token
        data = {"email": user.email}
        refresh_token = generate_token(JWT_REFRESH_TOKEN_EXPIRATION, data, os.environ['JWT_SECRET'])

        # Set the access and refresh token as a cookie in the response
        response = JSONResponse(content={"message": "Logged in", "encrypted_vault_key": res.encrypted_vault_key})
        response.set_cookie(key="refresh_token", value=refresh_token, max_age=JWT_REFRESH_TOKEN_EXPIRATION, samesite="none", secure=True, httponly=True, path="/log")
        return response

@app.get("/log/refresh")
def refresh(request : Request):

    # Get the refresh token from the request
    refresh_token = request.cookies.get("refresh_token")
    try:
        data = decrypt_token(refresh_token, os.environ['JWT_SECRET'])
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Generate a new access token
    access_token = generate_token(JWT_ACCESS_TOKEN_EXPIRATION, data, os.environ['JWT_SECRET'])

    # Set the access token as a cookie in the response
    response = JSONResponse(content={"message": "Token refreshed"})
    response.set_cookie(key="access_token", value=access_token, max_age=JWT_ACCESS_TOKEN_EXPIRATION, samesite="none", secure=True, httponly=True)

    return response

@app.get("/log/out")
def logout(request : Request):
    # Set the access and refresh token as a cookie in the response
    response = JSONResponse(content={"message": "Logged out"})
    if "access_token" in request.cookies:
        response.delete_cookie(key="access_token", samesite="none", secure=True, httponly=True)
    if "refresh_token" in request.cookies:
        response.delete_cookie(key="refresh_token", samesite="none", secure=True, httponly=True, path="/log")
    return response

########## Utils ##########

def verify_access_token(request: Request):
    # Verify the access token
    try:
        # Get the access token from the request
        access_token = request.cookies.get("access_token")
        data = decrypt_token(access_token, os.environ['JWT_SECRET'])
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid access token")
    return data

########## Protected Data Endpoints ##########

@app.get("/vault")
def vault(request : Request):
    # Verify the access token
    data = verify_access_token(request)
    # Get the user from the database
    user = db_client.user_by_email(data["email"])
    return {"key": user.encrypted_vault_key}

@app.get("/data")
def data(request: Request):
    # Verify the access token
    data = verify_access_token(request)
    # Get the user from the database
    user = db_client.user_by_email(data["email"])

    # Remove the authentication hash and encrypted vault key
    user.authentication_hash = None
    user.encrypted_vault_key = None

    # Get the banks from the database
    banks = db_client.get_banks(user)

    accounts = []
    # Get the accounts from the database
    for bank in banks:
        accounts += db_client.get_accounts(bank)

    transactions = []
    # Get the transactions from the database
    for account in accounts:
        transactions = db_client.get_transactions(account)

    return {"user": user, "banks": banks, "accounts": accounts, "transactions": transactions}

@app.post("/add_bank")
def add_bank(bank: Bank, request: Request):

    # Verify the access token
    data = verify_access_token(request)
    # Get the user from the database
    user = db_client.user_by_email(data['email'])

    # Save the bank
    inserted_id = db_client.save_bank(bank, user.id)
    
    return {"id": inserted_id}

## Endpoints to get the supported banks modules ##

@app.get("/banks")
def banks(request: Request):
    # Verify the access token
    _ = verify_access_token(request)
    wp = WebsiteProvider()
    return {"banks": wp.get_banks()}

@app.post("/websites")
def websites(bank: Bank, request: Request):
    # Verify the access token
    _ = verify_access_token(request)
    wp = WebsiteProvider()
    return {"websites": wp.get_websites(bank.name), }

@app.post("/login_format")
def login_website(bank: Bank, request: Request):
    # Verify the access token
    _ = verify_access_token(request)
    wp = WebsiteProvider()
    return {"login_format": wp.get_login_conditions(bank.name)}

@app.post("/password_format")
def password_website(bank: Bank, request: Request):
    # Verify the access token
    _ = verify_access_token(request)
    wp = WebsiteProvider()
    return {"password_format": wp.get_password_conditions(bank.name)}

