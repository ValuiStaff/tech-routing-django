#!/bin/bash

# Build and Push Docker Image to Docker Hub
# Run this script after starting Docker Desktop

set -e

echo "🐳 Building Docker image for Tech Routing App..."
cd "/Users/staffuser/Desktop/App Generation /django"

# Build image
docker build -t valuistaff/tech-routing:latest .

echo "✅ Image built successfully!"

# Tag image
docker tag valuistaff/tech-routing:latest valuistaff/tech-routing:v1.0

echo "📝 Image tagged: valuistaff/tech-routing:latest and v1.0"

# Login to Docker Hub (if not already logged in)
echo "🔐 Logging into Docker Hub..."
docker login

# Push to Docker Hub
echo "⬆️  Pushing image to Docker Hub..."
docker push valuistaff/tech-routing:latest
docker push valuistaff/tech-routing:v1.0

echo "✅ Successfully pushed to Docker Hub!"
echo ""
echo "🐳 Docker Hub: https://hub.docker.com/r/valuistaff/tech-routing"
echo ""
echo "📋 Next steps:"
echo "1. Go to Koyeb Dashboard"
echo "2. Create App → Deploy from Docker"
echo "3. Image: valuistaff/tech-routing:latest"
echo "4. Add environment variables"
echo "5. Deploy!"

