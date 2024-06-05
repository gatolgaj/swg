#!/bin/bash

# Load environment variables from .env file
export $(cat .env | xargs)

# Build the Docker image
echo "Building the Docker image..."
docker build -t swg .

# Run the Docker container
echo "Running the Docker container..."
docker run -d --name swg \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e QDRANT_URL=$QDRANT_URL \
  -e GOOGLE_APPLICATION_CREDENTIALS_JSON="service-account-key.json" \
  -p 8000:8000 swg

echo "Container is now running on http://localhost:8000"