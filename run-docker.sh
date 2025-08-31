#!/bin/bash

# Script to build and run the zendalona chatbot container

# Clean up space
echo "Cleaning up Docker space..."
docker system prune -f

# Remove existing image if it exists
echo "Removing existing image (if any)..."
docker rmi zendalona-chatbot 2>/dev/null

# Build the Docker image
echo "Building Docker image..."
docker build -t zendalona-chatbot .

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "Docker build failed. Exiting."
    exit 1
fi

# Stop and remove existing container if running
echo "Stopping existing container (if any)..."
docker stop zendalona-chatbot-container 2>/dev/null
docker rm zendalona-chatbot-container 2>/dev/null

# Run the container
echo "Running the container..."
docker run -d \
  --name zendalona-chatbot-container \
  --env-file .env \
  -p 8000:8000 \
  zendalona-chatbot

# Check if container started successfully
if [ $? -ne 0 ]; then
    echo "Failed to start container. Check logs with: docker logs zendalona-chatbot-container"
    exit 1
fi

echo "Container is running. Check logs with: docker logs zendalona-chatbot-container"
echo "API will be available at http://localhost:8000"