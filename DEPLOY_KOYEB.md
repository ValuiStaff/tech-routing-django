# Deploy to Koyeb - Complete Guide

## Quick Deploy

### Option 1: Deploy from GitHub (Recommended)

1. **Push your code to GitHub** (already done)

2. **Go to Koyeb Dashboard**
   - Visit: https://app.koyeb.com/
   - Sign up or log in

3. **Create a New App**
   - Click "Create App"
   - Select "Deploy from GitHub"
   - Authorize Koyeb to access your GitHub
   - Select repository: `ValuiStaff/tech-routing-django`
   - Select branch: `main`

4. **Configure Service**
   - **Build Command**: Leave empty (uses Dockerfile)
   - **Run Command**: Leave empty (uses Dockerfile CMD)
   
5. **Set Environment Variables**
   ```
   DJANGO_SETTINGS_MODULE=tech_routing.production_settings
   DEBUG=False
   SECRET_KEY=your-secret-key-here-generate-one
   GOOGLE_MAPS_API_KEY=your-google-maps-api-key
   DATABASE_URL=postgres://user:pass@host:port/dbname
   ```
   
   **Generate SECRET_KEY:**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

6. **Add PostgreSQL Database**
   - Click "Database" or "Create Database"
   - Select PostgreSQL
   - Koyeb will auto-populate `DATABASE_URL` env var

7. **Deploy**
   - Click "Deploy"
   - Wait for build to complete (~5-10 minutes)

## Option 2: Deploy via Koyeb CLI

1. **Install Koyeb CLI**
   ```bash
   brew install koyeb/tap/koyeb
   ```

2. **Login**
   ```bash
   koyeb auth login
   ```

3. **Deploy**
   ```bash
   cd /Users/staffuser/Desktop/App\ Generation\ /django
   koyeb app init tech-routing-django
   koyeb service create tech-routing-django \
     --app tech-routing-django \
     --git github.com/ValuiStaff/tech-routing-django \
     --git-branch main \
     --region us-east \
     --env "DJANGO_SETTINGS_MODULE=tech_routing.production_settings" \
     --env "DEBUG=False" \
     --env "SECRET_KEY=your-secret-key"
   ```

## Required Environment Variables

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=tech_routing.production_settings
DEBUG=False
SECRET_KEY=<generate-secret-key>

# Database (auto-configured if using Koyeb PostgreSQL)
DATABASE_URL=postgres://user:pass@host:port/db

# Google Maps API
GOOGLE_MAPS_API_KEY=<your-api-key>

# Optional - Performance
GUNICORN_WORKERS=3
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=120
PORT=8000
```

## Post-Deployment

1. **Create Superuser**
   ```bash
   koyeb app exec tech-routing-django
   python manage.py createsuperuser
   ```

2. **Access Admin Panel**
   - Go to `https://your-app.koyeb.app/admin`
   - Login with superuser credentials

3. **Configure Google Maps**
   - Go to Admin → Google Maps Config
   - Add your API key
   - Set average speed (default: 50 km/h)

## Troubleshooting

### Build Fails
- Check build logs in Koyeb dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Dockerfile syntax

### App Crashes
- Check app logs in Koyeb dashboard
- Verify environment variables are set
- Ensure database is connected

### Database Errors
- Check `DATABASE_URL` is correct
- Verify PostgreSQL is running
- Run migrations: `python manage.py migrate`

### Static Files Not Loading
- Already handled by WhiteNoise in production settings
- Check `STATIC_ROOT` is set correctly

## Resources

- Koyeb Docs: https://www.koyeb.com/docs
- Koyeb Dashboard: https://app.koyeb.com/
- GitHub Repository: https://github.com/ValuiStaff/tech-routing-django

