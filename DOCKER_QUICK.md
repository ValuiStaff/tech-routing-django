# Docker Hub Push - Quick Guide

## ⚠️ Start Docker Desktop First!

## Then Run:

```bash
cd "/Users/staffuser/Desktop/App Generation /django"

# Login to Docker Hub
docker login

# Build image
docker build -t valuistaff/tech-routing:latest .

# Tag
docker tag valuistaff/tech-routing:latest valuistaff/tech-routing:v1.0

# Push
docker push valuistaff/tech-routing:latest
docker push valuistaff/tech-routing:v1.0
```

## Or Use Automated Script:

```bash
cd "/Users/staffuser/Desktop/App Generation /django"
./build_and_push_docker.sh
```

## Deploy on Koyeb:

1. Go to https://app.koyeb.com/
2. Create App
3. Select "Deploy Docker"
4. Image: `valuistaff/tech-routing:latest`
5. Add PostgreSQL database
6. Add env vars
7. Deploy!

## Your Image Will Be:

🐳 **Docker Hub**: https://hub.docker.com/r/valuistaff/tech-routing

## Full Instructions:

See: `BUILD_DOCKER_MANUAL.md`

