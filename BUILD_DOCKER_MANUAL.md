# Build and Push Docker Image - Manual Instructions

## Prerequisites

### 1. Start Docker Desktop
- Open Docker Desktop application
- Wait for it to fully start (whale icon in menu bar)

### 2. Login to Docker Hub
```bash
docker login
```
Enter your Docker Hub credentials (create account at https://hub.docker.com if needed)

## Quick Build Script

Run the automated script:
```bash
cd "/Users/staffuser/Desktop/App Generation /django"
./build_and_push_docker.sh
```

## Manual Steps

### Step 1: Build Docker Image
```bash
cd "/Users/staffuser/Desktop/App Generation /django"
docker build -t valuistaff/tech-routing:latest .
```

This will take 3-5 minutes on first build.

### Step 2: Tag Image with Version
```bash
docker tag valuistaff/tech-routing:latest valuistaff/tech-routing:v1.0
```

### Step 3: Push to Docker Hub
```bash
# Push latest
docker push valuistaff/tech-routing:latest

# Push version
docker push valuistaff/tech-routing:v1.0
```

### Step 4: Verify
Visit: https://hub.docker.com/r/valuistaff/tech-routing

## Test Locally First

### Run Container
```bash
docker run -d \
  --name tech-routing-test \
  -p 8000:8000 \
  -e DATABASE_URL=sqlite:///db.sqlite3 \
  -e SECRET_KEY=test-secret-key \
  valuistaff/tech-routing:latest
```

### Access Application
- Open: http://localhost:8000
- Check health: http://localhost:8000/health/

### View Logs
```bash
docker logs -f tech-routing-test
```

### Stop Container
```bash
docker stop tech-routing-test
docker rm tech-routing-test
```

## Deploy on Koyeb with Docker Hub Image

### Step 1: Go to Koyeb
Visit: https://app.koyeb.com/

### Step 2: Create App
1. Click "Create App"
2. Select "Deploy a Docker image"
3. Enter image: `valuistaff/tech-routing:latest`
4. Click "Deploy"

### Step 3: Add PostgreSQL Database
1. Click "Add Database"
2. Select "PostgreSQL"
3. Koyeb auto-configures `DATABASE_URL`

### Step 4: Environment Variables
Add these in Koyeb dashboard:
```bash
DJANGO_SETTINGS_MODULE=tech_routing.production_settings
DEBUG=False
SECRET_KEY=<generate-with-command-below>
GOOGLE_MAPS_API_KEY=<your-api-key>
PORT=8000
```

Generate SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 5: Deploy!
Click "Deploy" and wait 2-5 minutes.

## Image Information

**Docker Hub Repository**: `valuistaff/tech-routing`

**Tags Available**:
- `latest` - Always points to latest version
- `v1.0` - Specific version

**Image Details**:
- Base: `python:3.10-slim`
- Size: ~500MB
- Includes: All dependencies, app code, static files

## Troubleshooting

### "Cannot connect to Docker daemon"
**Solution**: Start Docker Desktop application

### "Access Denied"
**Solution**: 
1. Run `docker login`
2. Check Docker Hub permissions

### "Build failed"
**Solution**: Check build logs for errors

### "Image not found"
**Solution**: Ensure you've pushed the image:
```bash
docker push valuistaff/tech-routing:latest
```

## Complete Commands Summary

```bash
# Start Docker Desktop first!

# Build
docker build -t valuistaff/tech-routing:latest .

# Tag
docker tag valuistaff/tech-routing:latest valuistaff/tech-routing:v1.0

# Login
docker login

# Push
docker push valuistaff/tech-routing:latest
docker push valuistaff/tech-routing:v1.0
```

## Next Steps After Push

1. ✅ Image pushed to Docker Hub
2. Go to Koyeb Dashboard
3. Create new app
4. Select your Docker image
5. Add PostgreSQL database
6. Set environment variables
7. Deploy!

Your app will be live at: `https://your-app.koyeb.app`

