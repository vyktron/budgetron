
# Use the official Python base image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /model

# Upgrade pip
RUN pip install --upgrade pip
# Install the required Python packages
RUN pip install woob requests uvicorn fastapi scrypt pymongo pyjwt cryptography

# Copy the application code to the container
COPY ./model ./model
COPY ./etc/key.pem ./etc/key.pem
COPY ./etc/cert.pem ./etc/cert.pem

# Start the FastAPI server
CMD ["uvicorn", "model.api:app", "--host", "0.0.0.0", "--port", "8089", "--ssl-keyfile", "etc/key.pem", "--ssl-certfile", "etc/cert.pem"]