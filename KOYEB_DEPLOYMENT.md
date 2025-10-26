# Deploy to Koyeb - Complete Guide

## What is Koyeb?

Koyeb is a serverless platform that makes deploying applications easy:
- ✅ Free tier available (with limits)
- ✅ Automatic HTTPS
- ✅ Zero-config deployments
- ✅ Built-in Git integration
- ✅ Global edge network
- ✅ Auto-scaling

## Prerequisites

1. **GitHub Repository**: Your code is already on GitHub at https://github.com/ValuiStaff/tech-routing-django
2. **Koyeb Account**: Sign up at https://www.koyeb.com/ (free)

## Quick Deployment Steps

### Step 1: Sign Up for Koyeb

1. Go to: https://www.koyeb.com/
2. Click "Sign Up"
3. Create account (free tier available)
4. Verify your email

### Step 2: Connect GitHub

1. In Koyeb dashboard, click **"Create Service"**
2. Select **"GitHub"** as deployment source
3. Authorize Koyeb to access your GitHub
4. Select repository: `ValuiStaff/tech-routing-django`
5. Select branch: `main`

### Step 3: Configure Your App

**Build Configuration**:
- **Build Command**: (leave empty or set if needed)
- **Run Command**: `gunicorn tech_routing.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4`
- **Port**: Koyeb auto-detects or use `$PORT` environment variable

**Environment Variables**:
Add these in the configuration:

```
DJANGO_SETTINGS_MODULE=tech_routing.production_settings
DEBUG=False
SECRET_KEY=your-secret-key-change-this
GOOGLE_MAPS_API_KEY=AIzaSyCZCEanL50XqkGdej2VdZUCwRrkcf1RrYw
PYTHON_VERSION=3.10
```

**Database**:
For Koyeb, you can use:
- **Option A**: External PostgreSQL (recommended)
  - Use https://www.neon.tech/ (free) or https://www.elephantsql.com/ (free)
- **Option B**: SQLite (not recommended for production but works)

If using external PostgreSQL:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### Step 4: Deploy

1. Click **"Deploy"**
2. Wait 3-5 minutes for deployment
3. Your app will be live at: `your-app-name.koyeb.app`

### Step 5: Post-Deployment Setup

Once deployed:

1. **Access your app**: Visit the URL Koyeb provides
2. **Run migrations**: Use Koyeb's console or SSH:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py populate_test_data
   ```

## Koyeb-Specific Configuration

### Update production_settings.py

Since Koyeb uses dynamic port binding, make sure your settings handle the PORT variable:

```python
# In tech_routing/production_settings.py
ALLOWED_HOSTS = ['*']  # Or add your specific domain

# Dynamic port handling
import os
PORT = os.environ.get('PORT', 8000)

# Database - use the DATABASE_URL from Koyeb
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}
```

### Create nixpacks.toml (Optional)

If you want custom build configuration:

```toml
[providers]
nixpacks = { image = "python" }

[static-assets]
static = "/static"

[processes]
web = "gunicorn tech_routing.wsgi:application --bind 0.0.0.0:$PORT"
```

### Create Procfile (Alternative)

Create a `Procfile` in your project root:

```
web: gunicorn tech_routing.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
```

## Database Setup

### Option 1: External PostgreSQL (Recommended)

1. **Sign up for Neon** (free PostgreSQL): https://www.neon.tech/
2. **Create database** for your project
3. **Copy connection string**
4. **Add to Koyeb environment variables**:
   ```
   DATABASE_URL=postgresql://user:pass@host/dbname
   ```

### Option 2: SQLite (Quick Start)

Works for development/testing but not production:

```python
# In production_settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

⚠️ **Warning**: SQLite can lose data on Koyeb if the container restarts.

## Requirements.txt for Koyeb

Make sure your `requirements.txt` includes:

```
Django==5.2.7
googlemaps==4.10.0
ortools==9.14.6206
pandas==2.3.3
numpy==2.3.4
openpyxl==3.1.5
django-crispy-forms==2.4
crispy-bootstrap5==2025.6
gunicorn==21.2.0
psycopg2-binary==2.9.9
whitenoise==6.6.0
```

## Deployment Benefits

**Koyeb Advantages:**
- ✅ Free tier (with limitations)
- ✅ Automatic HTTPS
- ✅ Zero-config (mostly)
- ✅ Git-based deployment
- ✅ Auto-scaling
- ✅ Global edge network
- ✅ Easy to use

**Koyeb Free Tier Limits:**
- Limited requests/month
- Basic resources
- May need paid plan for production traffic

## Troubleshooting

### App Won't Start

**Check logs in Koyeb dashboard:**
1. Go to your service
2. Click "Logs"
3. Look for errors

**Common issues:**
- Missing environment variables
- Database connection errors
- Port binding issues

### Database Errors

**Run migrations via Koyeb console:**
1. Go to Service → Console
2. Run: `python manage.py migrate`
3. Run: `python manage.py createsuperuser`

### Static Files Not Loading

**Add to requirements.txt:**
```
whitenoise==6.6.0
```

**Update settings.py:**
```python
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... rest of middleware
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Google Maps Not Working

1. Check API key is set in environment variables
2. Enable APIs in Google Cloud Console:
   - Maps JavaScript API
   - Places API
   - Geocoding API
   - Distance Matrix API

## Monitoring

**Koyeb Dashboard:**
- View logs in real-time
- Monitor resource usage
- Check deployment history
- View metrics

## Custom Domain

1. **In Koyeb dashboard**, go to your service
2. **Click**: "Domains"
3. **Add domain**: your-domain.com
4. **Update DNS** with the CNAME provided
5. **Update** ALLOWED_HOSTS in settings

## Cost Comparison

**Koyeb**:
- Free tier (limited)
- Paid plans start at $25/month
- Includes: database, scaling, edge network

**DigitalOcean**:
- $12-20/month for basic setup
- More control
- Manual configuration

**Recommendation**: Koyeb is easier, but DigitalOcean gives more control.

## Next Steps

1. ✅ Push code to GitHub (already done)
2. ✅ Sign up for Koyeb
3. ✅ Deploy your app
4. ✅ Set up database
5. ✅ Configure environment variables
6. ✅ Test your app!

## Your Repository

GitHub: https://github.com/ValuiStaff/tech-routing-django

All files are ready for Koyeb deployment!

## Alternative: One-Click Deploy

If you have the Koyeb CLI (optional):

```bash
# Install Koyeb CLI
curl -fsSL https://www.koyeb.com/install | sh

# Deploy
koyeb app create django-tech-routing \
  --git https://github.com/ValuiStaff/tech-routing-django.git

# Update environment
koyeb secrets create --from-literal SECRET_KEY="your-key"
```

## Support

- Koyeb Docs: https://www.koyeb.com/docs/
- Koyeb Support: https://www.koyeb.com/support
- Your app is ready! 🚀

