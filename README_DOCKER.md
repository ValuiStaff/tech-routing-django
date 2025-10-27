# Tech Routing App - Docker Deployment

## 🚀 Quick Start

### Push to Docker Hub

**Start Docker Desktop first!**

Then run:
```bash
cd "/Users/staffuser/Desktop/App Generation /django"
./build_and_push_docker.sh
```

Or manually:
```bash
docker login
docker build -t valuistaff/tech-routing:latest .
docker tag valuistaff/tech-routing:latest valuistaff/tech-routing:v1.0
docker push valuistaff/tech-routing:latest
docker push valuistaff/tech-routing:v1.0
```

## 📦 What's Included

✅ **Dockerfile** - Optimized for production
✅ **Build Script** - Automated build and push
✅ **Deployment Guides** - Step-by-step instructions
✅ **Health Check** - `/health/` endpoint
✅ **Auto-migrations** - Runs on container start
✅ **Static Files** - Pre-collected
✅ **PostgreSQL Support** - Database URL parsing
✅ **SQLite Fallback** - Works without external DB

## 📂 Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Production Docker image definition |
| `build_and_push_docker.sh` | Automated build/push script |
| `BUILD_DOCKER_MANUAL.md` | Manual build instructions |
| `DOCKER_QUICK.md` | Quick reference |
| `DOCKER_HUB_DEPLOY.md` | Complete deployment guide |
| `.dockerignore` | Excludes venv, cache, etc. |

## 🎯 Deploy on Koyeb

1. Build and push to Docker Hub (see above)
2. Go to https://app.koyeb.com/
3. Create App → Deploy Docker
4. Image: `valuistaff/tech-routing:latest`
5. Add PostgreSQL database
6. Set environment variables:
   - `SECRET_KEY`
   - `GOOGLE_MAPS_API_KEY`
7. Deploy!

## 🌐 Image Info

- **Repository**: `valuistaff/tech-routing`
- **Latest**: `valuistaff/tech-routing:latest`
- **Version**: `valuistaff/tech-routing:v1.0`
- **Size**: ~500MB
- **Base**: Python 3.10-slim

## 📋 Environment Variables

```bash
DJANGO_SETTINGS_MODULE=tech_routing.production_settings
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/dbname
GOOGLE_MAPS_API_KEY=your-api-key
GUNICORN_WORKERS=3
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=120
PORT=8000
```

## 🧪 Test Locally

```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=sqlite:///db.sqlite3 \
  -e SECRET_KEY=test \
  valuistaff/tech-routing:latest

# Visit http://localhost:8000
```

## 📚 More Help

- **Docker Guide**: `BUILD_DOCKER_MANUAL.md`
- **Koyeb Guide**: `KOYEB_QUICK_START.md`
- **Local Test**: `LOCAL_TEST_GUIDE.md`
- **GitHub**: https://github.com/ValuiStaff/tech-routing-django

## ✨ Features

- Django 5.2.7
- PostgreSQL support with SQLite fallback
- OR-Tools job assignment
- Google Maps integration
- Multi-role authentication
- Bootstrap 5 UI
- Health check endpoint
- Automatic migrations
- WhiteNoise for static files

## 🎉 Ready to Deploy!

All code is on GitHub and ready for Docker Hub!

