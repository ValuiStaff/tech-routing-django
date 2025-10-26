# PythonAnywhere Deployment Guide

This guide will walk you through deploying your Django Technician Routing Application to PythonAnywhere.

## Prerequisites

- A PythonAnywhere account (free tier works: https://www.pythonanywhere.com/)
- Your Google Maps API key
- All dependencies listed in `requirements.txt`

## Step 1: Account Setup

1. Go to https://www.pythonanywhere.com/
2. Create a free account (or log in if you already have one)
3. Once logged in, you'll see the Dashboard

## Step 2: Upload Your Code

### Option A: Using the PythonAnywhere Files Interface (Easiest)

1. Click **Files** tab in the PythonAnywhere web interface
2. Navigate to: `/home/yourusername/` (replace `yourusername` with your actual username)
3. Click **Upload a file** and upload your entire Django project folder

Or upload via Terminal:
```bash
# In PythonAnywhere Bash console
cd /home/yourusername/
mkdir tech_routing
cd tech_routing
# Upload files using wget or curl, or use the Files tab
```

### Option B: Using Git (Recommended for Updates)

```bash
# In PythonAnywhere Bash console
cd /home/yourusername/
git clone YOUR_GITHUB_REPO_URL tech_routing
cd tech_routing
# Or upload via zip and extract
```

## Step 3: Create Virtual Environment

1. Open **Consoles** tab in PythonAnywhere
2. Start a **Bash** console
3. Run:

```bash
cd /home/yourusername/tech_routing
python3.10 -m venv venv  # or python3.9 depending on what's available
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: PythonAnywhere free accounts support Python 3.9 and 3.10. Use whichever is available.

## Step 4: Configure Django Settings

Edit the files to match your PythonAnywhere setup:

1. Update `tech_routing/settings.py`:
   - Change `ALLOWED_HOSTS` to include your domain
   - Update `STATIC_ROOT` and `MEDIA_ROOT` paths
   
2. Or use the provided `pythonanywhere_settings.py`:

In your `settings.py`, add at the bottom:
```python
# Import PythonAnywhere settings if available
try:
    from .pythonanywhere_settings import ON_PYTHONANYWHERE
    if ON_PYTHONANYWHERE:
        from .pythonanywhere_settings import *
except ImportError:
    pass
```

3. **Important**: Update paths in `pythonanywhere_settings.py`:
   - Replace `'yourusername'` with your actual PythonAnywhere username
   - Update `ALLOWED_HOSTS` with your domain

## Step 5: Run Database Migrations

In the PythonAnywhere Bash console:

```bash
cd /home/yourusername/tech_routing
source venv/bin/activate
python manage.py migrate
```

## Step 6: Create Superuser

```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

## Step 7: Populate Test Data (Optional)

```bash
python manage.py populate_test_data
```

This creates sample users, technicians, and service requests for testing.

## Step 8: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

This collects all static files to the `STATIC_ROOT` directory.

## Step 9: Create Media and Logs Directories

```bash
mkdir -p /home/yourusername/tech_routing/media
mkdir -p /home/yourusername/tech_routing/logs
mkdir -p /home/yourusername/tech_routing/static
```

## Step 10: Configure Web App

1. Click **Web** tab in PythonAnywhere dashboard
2. Click **Add a new web app**
3. Choose **Manual Configuration** (don't use the automatic Django wizard)
4. Select your Python version (3.9 or 3.10)

### Edit the WSGI File

PythonAnywhere will provide a default WSGI file. Edit it:

```python
# /var/www/yourusername_pythonanywhere_com_wsgi.py

import os
import sys

path = '/home/yourusername/tech_routing'  # Update this path!
if path not in sys.path:
    sys.path.append(path)

# Set up Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'tech_routing.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Update the path to point to your actual project directory!

### Configure Static Files

In the **Static files** section of the Web tab:

- URL: `/static/`
- Directory: `/home/yourusername/tech_routing/static`

- URL: `/media/`
- Directory: `/home/yourusername/tech_routing/media`

## Step 11: Configure Environment Variables

### Set Google Maps API Key

You can set this in the WSGI file or in Django settings:

```python
# In your settings.py or pythonanywhere_settings.py
GOOGLE_MAPS_API_KEY = "YOUR_API_KEY_HERE"
```

Or set it in the Web app's WSGI file before `get_wsgi_application()`:

```python
os.environ['GOOGLE_MAPS_API_KEY'] = 'YOUR_API_KEY_HERE'
```

## Step 12: Reload Web App

1. Go to **Web** tab
2. Click the **Reload** button (green)
3. Your app should now be running!

## Step 13: Access Your Application

Visit: `https://yourusername.pythonanywhere.com/`

You should see your Django application running!

## Test the Deployment

1. Visit: `https://yourusername.pythonanywhere.com/admin/`
2. Log in with your superuser credentials
3. Check that models are visible
4. Configure Google Maps API key in admin panel
5. Test each role:
   - Admin dashboard
   - Customer signup/registration
   - Technician signup
   - Job assignment (OR-Tools)
   - Map views

## Troubleshooting

### Error: ModuleNotFoundError

Make sure your virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Static Files Not Loading

- Check that `collectstatic` was run
- Verify static file paths in Web tab
- Check file permissions: `chmod -R 755 static/`

### Database Errors

- Make sure migrations ran: `python manage.py migrate`
- Check database permissions
- For free accounts, SQLite works well

### Google Maps Not Working

- Verify API key is set correctly
- Check browser console for errors
- Ensure API is enabled in Google Cloud Console:
  - Maps JavaScript API
  - Places API
  - Geocoding API
  - Distance Matrix API

### App Reloads but Shows Error Page

- Check the **Error log** in the Web tab
- Common issues:
  - Wrong paths in WSGI file
  - Import errors
  - Missing settings

## Updating Your App

When you make changes:

1. Upload updated files
2. Run migrations if needed: `python manage.py migrate`
3. Collect static files: `python manage.py collectstatic --noinput`
4. Reload web app in PythonAnywhere dashboard

## Performance Tips

### For Free Tier

- SQLite database (included)
- 512MB disk space
- 100 second CPU time per request
- Limited to 3 seconds of web requests

### Consider Upgrading If

- You need PostgreSQL (paid tier)
- You have many concurrent users
- You need more disk space
- You want custom domain

## Security Checklist

- [ ] `DEBUG = False` in production
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] Secret key is secure (don't commit to version control)
- [ ] HTTPS enabled (automatic on PythonAnywhere)
- [ ] Google Maps API key restricted in Google Cloud Console

## Domain Configuration (Optional - Paid Feature)

If you have a paid PythonAnywhere account and custom domain:

1. Add domain in **Web** tab
2. Configure DNS records for your domain
3. Update `ALLOWED_HOSTS` to include your domain
4. Reload web app

## Support

- PythonAnywhere Help: https://www.pythonanywhere.com/help/
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- Check error logs in PythonAnywhere Web tab for specific errors

## Deployment Checklist

- [ ] Created PythonAnywhere account
- [ ] Uploaded code files
- [ ] Created virtual environment and installed dependencies
- [ ] Updated paths in settings (yourusername)
- [ ] Ran database migrations
- [ ] Created superuser account
- [ ] Populated test data (optional)
- [ ] Collected static files
- [ ] Configured WSGI file
- [ ] Set up static/media files mapping
- [ ] Configured Google Maps API key
- [ ] Reloaded web app
- [ ] Tested all functionality
- [ ] Verified HTTPS works
- [ ] Checked error logs

**Congratulations! Your Django application is now live!** 🎉

