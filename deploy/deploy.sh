#!/bin/bash

# Deployment script for production

set -e  # Exit on any error

echo "Starting deployment process..."

# Configuration
APP_NAME="hackrx-api"
DOCKER_IMAGE="hackrx-api:latest"
CONTAINER_NAME="hackrx-api-container"

# Build Docker image
echo "Building Docker image..."
docker build -t $DOCKER_IMAGE .

# Stop existing container if running
echo "Stopping existing container..."
docker stop $CONTAINER_NAME || true
docker rm $CONTAINER_NAME || true

# Run new container
echo "Starting new container..."
docker run -d \
  --name $CONTAINER_NAME \
  --restart unless-stopped \
  -p 8000:8000 \
  -e DATABASE_URL="$DATABASE_URL" \
  -e OLLAMA_BASE_URL="$OLLAMA_BASE_URL" \
  -e API_TOKEN="$API_TOKEN" \
  -v /app/data:/app/data \
  $DOCKER_IMAGE

# Health check
echo "Performing health check..."
sleep 10

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Deployment successful! API is healthy."
else
    echo "❌ Deployment failed! API health check failed."
    exit 1
fi

# Cleanup old images
echo "Cleaning up old Docker images..."
docker image prune -f

echo "Deployment completed successfully!"