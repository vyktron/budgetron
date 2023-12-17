
# Use the official Python base image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /model

# Upgrade pip
RUN pip install --upgrade pip
# Install the required Python packages
RUN pip install woob requests uvicorn fastapi scrypt pymongo pyjwt

# Copy the application code to the container
COPY ./model ./model
COPY ./etc/server.crt ./etc/server.crt
COPY ./etc/server.key ./etc/server.key

# Start the FastAPI server
CMD ["uvicorn", "model.api:app", "--host", "0.0.0.0", "--port", "8089", "--ssl-keyfile", "etc/server.key", "--ssl-certfile", "etc/server.crt"]