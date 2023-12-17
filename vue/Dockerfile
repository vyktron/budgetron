# Specify the base image
FROM node:alpine

# Set the working directory
WORKDIR /vue

# Copy the rest of the application code to the working directory
COPY . /vue

# Install dependencies
RUN cd /vue

# Start the application
CMD [ "npm", "run", "dev", "--", "--host"]
