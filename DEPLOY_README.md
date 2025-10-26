# Deploy Your Django App to PythonAnywhere - Quick Guide

## 📋 What You Need

1. PythonAnywhere account (free): https://www.pythonanywhere.com/
2. Your Google Maps API key
3. All files from this project

## 🚀 Quick Deployment Steps

### Step 1: Create PythonAnywhere Account

1. Go to https://www.pythonanywhere.com/
2. Click "Sign up" and create a free account
3. Note your username (e.g., "myusername")

### Step 2: Upload Your Code

**Option A - Using PythonAnywhere Files Interface:**
1. Click **Files** tab in PythonAnywhere
2. Upload all project files to `/home/yourusername/tech_routing/`

**Option B - Using Bash Console:**
```bash
# In PythonAnywhere bash console
cd /home/yourusername/
git clone YOUR_REPO_URL tech_routing
```

### Step 3: Setup Virtual Environment

```bash
cd /home/yourusername/tech_routing
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Configure Settings

Edit `tech_routing/pythonanywhere_settings.py`:
- Replace `'yourusername'` with your actual username
- Update `ALLOWED_HOSTS` with your domain

### Step 5: Run Setup Commands

```bash
# In activated virtualenv
python manage.py migrate
python manage.py createsuperuser
python manage.py populate_test_data  # Optional test data
python manage.py collectstatic --noinput
```

### Step 6: Configure Web App

1. Go to **Web** tab in PythonAnywhere
2. Click **Add a new web app** → **Manual Configuration**
3. Select Python version (3.10 or 3.9)
4. Edit WSGI file:

```python
import os
import sys

path = '/home/yourusername/tech_routing'  # Update this!
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'tech_routing.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5. Configure Static Files (in Web tab):
   - URL: `/static/` → Directory: `/home/yourusername/tech_routing/static`
   - URL: `/media/` → Directory: `/home/yourusername/tech_routing/media`

### Step 7: Set API Key

In WSGI file or settings, add:
```python
os.environ['GOOGLE_MAPS_API_KEY'] = 'YOUR_API_KEY_HERE'
```

### Step 8: Reload and Test

1. Click **Reload** button in Web tab
2. Visit: `https://yourusername.pythonanywhere.com/`
3. Test all features!

## 📚 Full Documentation

- **Detailed Guide**: `PYTHONANYWHERE_DEPLOYMENT.md`
- **Checklist**: `DEPLOYMENT_CHECKLIST.txt`

## 🐛 Troubleshooting

**Module Not Found?**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Static Files Not Working?**
```bash
python manage.py collectstatic --noinput
```

**Database Errors?**
```bash
python manage.py migrate
```

**Still having issues?**
- Check error logs in PythonAnywhere Web tab
- Check file paths are correct
- Make sure virtualenv is activated

## ✅ What Should Work After Deployment

- ✓ Home page loads
- ✓ Admin panel accessible
- ✓ Customer registration
- ✓ Technician signup
- ✓ Job assignment (OR-Tools)
- ✓ Map visualization
- ✓ Google Places autocomplete
- ✓ All role-based dashboards

## 🎉 You're Live!

Visit: `https://yourusername.pythonanywhere.com/`

**Need Help?**
- PythonAnywhere Docs: https://www.pythonanywhere.com/help/
- Check PYTHONANYWHERE_DEPLOYMENT.md for detailed steps

