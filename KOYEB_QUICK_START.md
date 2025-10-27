# Koyeb Deployment - Quick Start Guide

## Your app is ready to deploy! 🚀

All files have been pushed to GitHub: https://github.com/ValuiStaff/tech-routing-django

## Deploy in 5 Minutes

### Step 1: Go to Koyeb
Visit: https://app.koyeb.com/signup

### Step 2: Create New App
1. Click **"Create App"**
2. Click **"Deploy from GitHub"**
3. Authorize Koyeb to access GitHub
4. Select repository: `ValuiStaff/tech-routing-django`
5. Select branch: `main`

### Step 3: Configure Build
- **Type**: Dockerfile (auto-detected)
- **Build Command**: Leave empty
- **Run Command**: Leave empty

### Step 4: Add PostgreSQL Database
1. Scroll to **"Add Database"**
2. Click **"Create PostgreSQL Database"**
3. Koyeb will auto-add `DATABASE_URL` environment variable

### Step 5: Set Environment Variables
Click **"Environment Variables"** and add:

```bash
# Required
DJANGO_SETTINGS_MODULE=tech_routing.production_settings
DEBUG=False
SECRET_KEY=<generate-this-key>

# Get SECRET_KEY by running:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Your Google Maps API Key
GOOGLE_MAPS_API_KEY=AIzaSy-your-key-here

# Optional - Performance tuning
GUNICORN_WORKERS=3
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=120
```

### Step 6: Deploy!
Click **"Deploy"** and wait ~5-10 minutes

### Step 7: Create Admin User
Once deployed, access your app at: `https://your-app-name.koyeb.app`

Open a terminal in your app (Koyeb dashboard → App → Exec) and run:

```bash
python manage.py createsuperuser
```

Enter username, email, and password.

## Post-Deployment Setup

1. **Access Admin**: `https://your-app-name.koyeb.app/admin`
2. **Login** with superuser credentials
3. **Configure Google Maps**:
   - Go to: Admin → Core → Google Maps Configs
   - Add your API key
   - Set average speed: 50 km/h
4. **Add Skills**:
   - Go to: Admin → Core → Skills
   - Add skills: "gas", "electric", "plumbing", "hvac"
5. **Create Test Users**:
   - Admin → Accounts → Users
   - Create customer accounts
   - Create technician accounts

## What Was Fixed

✅ **Simplified Dockerfile** - Single stage build for Koyeb
✅ **Production Settings** - Proper PostgreSQL parsing and SQLite fallback
✅ **Health Check Endpoint** - `/health/` endpoint for monitoring
✅ **WhiteNoise Integration** - Serves static files automatically
✅ **Database Migrations** - Run automatically on startup
✅ **Environment Variables** - Proper parsing and defaults
✅ **Procfile** - For Heroku/Koyeb compatibility

## Troubleshooting

### Build fails?
- Check logs in Koyeb dashboard
- Ensure `DATABASE_URL` is set (auto-set if PostgreSQL is added)

### App crashes?
- Check logs: App → Logs
- Verify all environment variables are set
- Ensure SECRET_KEY is set

### Can't access admin?
- Run migrations: `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`

### Static files not loading?
- Handled automatically by WhiteNoise
- Check console for errors

## Support

- Koyeb Docs: https://www.koyeb.com/docs
- Your Repo: https://github.com/ValuiStaff/tech-routing-django

## Need Help?

Check the detailed guide: `DEPLOY_KOYEB.md`

