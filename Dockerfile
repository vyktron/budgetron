
# Use the official Python base image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /model

# Upgrade pip
RUN pip install --upgrade pip
# Install the required Python packages
RUN pip install woob requests uvicorn fastapi scrypt pymongo pyjwt

# Copy the application code to the container
COPY . ./model

# Start the FastAPI server
CMD ["uvicorn", "model.api:app", "--host", "0.0.0.0", "--port", "8089"]
