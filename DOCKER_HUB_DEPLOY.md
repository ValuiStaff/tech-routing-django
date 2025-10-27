# Deploy to Docker Hub - Complete Guide

## Docker Hub Setup

### Step 1: Login to Docker Hub
```bash
docker login
```

Enter your Docker Hub credentials.

### Step 2: Build the Image
```bash
cd "/Users/staffuser/Desktop/App Generation /django"
docker build -t valuistaff/tech-routing:latest .
```

### Step 3: Tag for Docker Hub
```bash
docker tag tech-routing:latest valuistaff/tech-routing:latest
docker tag tech-routing:latest valuistaff/tech-routing:v1.0
```

### Step 4: Push to Docker Hub
```bash
docker push valuistaff/tech-routing:latest
docker push valuistaff/tech-routing:v1.0
```

## Test Locally

### Run Container
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/dbname \
  -e SECRET_KEY=your-secret-key \
  -e GOOGLE_MAPS_API_KEY=your-api-key \
  valuistaff/tech-routing:latest
```

### Access Application
- URL: http://localhost:8000
- Health: http://localhost:8000/health/

### Check Logs
```bash
docker logs -f <container-id>
```

## Deploy on Koyeb with Docker Hub

1. Go to https://app.koyeb.com/
2. Create App → Deploy → Docker
3. Image: `valuistaff/tech-routing:latest`
4. Add environment variables
5. Deploy!

## Image Info

- **Image Name**: `valuistaff/tech-routing`
- **Latest Tag**: `latest`
- **Version Tag**: `v1.0`
- **Base Image**: `python:3.10-slim`
- **Size**: ~500MB

## Environment Variables

```bash
DJANGO_SETTINGS_MODULE=tech_routing.production_settings
DEBUG=False
SECRET_KEY=<your-secret-key>
DATABASE_URL=postgresql://user:pass@host:5432/dbname
GOOGLE_MAPS_API_KEY=<your-api-key>
GUNICORN_WORKERS=3
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=120
PORT=8000
```

