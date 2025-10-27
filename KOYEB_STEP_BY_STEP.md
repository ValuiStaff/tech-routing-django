# Deploy to Koyeb - Step by Step Guide

## Prerequisites

✅ Your code is on GitHub: `ValuiStaff/tech-routing-django`  
✅ You have a Koyeb account  
✅ You have a Google Maps API key  

## Step 1: Generate SECRET_KEY

Open terminal and run:

```bash
cd "/Users/staffuser/Desktop/App Generation /django"
source venv/bin/activate
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Copy this SECRET_KEY** - you'll need it in Step 3!

## Step 2: Go to Koyeb Dashboard

1. Visit: https://app.koyeb.com/
2. Sign up or log in with your account
3. You'll see the Koyeb dashboard

## Step 3: Create Your App

1. **Click "Create App"** button (top right)
2. Select **"Deploy from GitHub"**
3. Authorize Koyeb to access your GitHub (if not already done)
4. Select repository: **`ValuiStaff/tech-routing-django`**
5. Select branch: **`main`**
6. Click **"Next"**

## Step 4: Configure Build

### Build Settings:
- **Build Command**: Leave EMPTY (Dockerfile handles it)
- **Run Command**: Leave EMPTY (Dockerfile CMD handles it)
- **Dockerfile**: Auto-detected ✅

### Click "Next"

## Step 5: Add PostgreSQL Database

1. Scroll down to **"Services"** section
2. Click **"Add Service"** or **"Add Database"**
3. Select **"PostgreSQL"**
4. Configure:
   - **Name**: `tech-routing-db` (or any name you like)
   - **Region**: Choose closest to you (e.g., `us-east`)
   - **Plan**: Starter ($5/month) or Free tier
5. Click **"Create"**

**Koyeb will automatically:**
- ✅ Create PostgreSQL database
- ✅ Add `DATABASE_URL` environment variable
- ✅ Connect it to your app

## Step 6: Set Environment Variables

### Click "Environment Variables" or "Variables" tab

Add these variables:

| Variable Name | Value |
|--------------|-------|
| `DJANGO_SETTINGS_MODULE` | `tech_routing.production_settings` |
| `DEBUG` | `False` |
| `SECRET_KEY` | `paste-your-generated-key-here` |
| `GOOGLE_MAPS_API_KEY` | `your-google-maps-api-key` |

### How to add each variable:

1. Click **"Add Variable"**
2. Enter variable name and value
3. Click **"Save"**
4. Repeat for each variable

**Example:**
```
Variable: DJANGO_SETTINGS_MODULE
Value: tech_routing.production_settings
```

## Step 7: Deploy!

1. **Click "Deploy"** button
2. Wait 5-10 minutes for build to complete
3. Watch the logs (they'll show progress)

### You'll see:
- ✅ Building Docker image
- ✅ Installing dependencies
- ✅ Collecting static files
- ✅ Running migrations
- ✅ Starting server

## Step 8: Wait for Deployment

- Build time: 5-10 minutes
- You'll get a green checkmark when done
- Your app URL will be: `https://your-app-name.koyeb.app`

## Step 9: Import Your Data (Optional)

If you want to import local data:

### Access Koyeb Shell:

1. Go to your app dashboard
2. Click **"Exec"** button or **"Shell"** button
3. Terminal will open

### Run these commands:

```bash
# Navigate to app directory
cd /app

# Run migrations (if not already done)
python manage.py migrate --noinput

# Import your local data
python manage.py loaddata production_data.json

# Create superuser (if not in imported data)
python manage.py createsuperuser
```

## Step 10: Verify Deployment

### Check Your App:

1. Visit: `https://your-app-name.koyeb.app`
2. You should see your home page
3. Try logging in:
   - If you imported data: use your local credentials
   - If not: create a superuser first

### Check Health Endpoint:

Visit: `https://your-app-name.koyeb.app/health/`

Should return: `{"status": "ok", "service": "tech-routing"}`

## Step 11: Configure Google Maps

1. Go to: `https://your-app-name.koyeb.app/admin`
2. Login with superuser credentials
3. Navigate to: **Core → Google Maps Configs**
4. Click on the existing config
5. Enter your Google Maps API key
6. Set Average Speed: `50` km/h
7. Save

## Complete Environment Variables Summary

Here's what you should have set in Koyeb:

```bash
# Django Configuration
DJANGO_SETTINGS_MODULE=tech_routing.production_settings
DEBUG=False
SECRET_KEY=<your-generated-secret-key>

# Google Maps
GOOGLE_MAPS_API_KEY=<your-google-maps-api-key>

# Database (Auto-added by PostgreSQL service)
DATABASE_URL=postgres://user:pass@host:port/dbname
```

## Troubleshooting

### Deployment Fails?

1. **Check build logs** in Koyeb dashboard
2. Look for error messages
3. Common issues:
   - Missing environment variables
   - PostgreSQL not created
   - Invalid SECRET_KEY

### Database Connection Error?

1. Verify PostgreSQL service is running
2. Check `DATABASE_URL` is set correctly
3. Wait a few minutes for database to initialize

### App Crashes?

1. Click on your app in dashboard
2. Go to **"Logs"** tab
3. Read error messages
4. Common causes:
   - Missing `GOOGLE_MAPS_API_KEY`
   - Invalid `SECRET_KEY`
   - Database connection issues

### Static Files Not Loading?

- Already handled by WhiteNoise ✅
- Should work automatically

## After Deployment

### Your App is Live! 🎉

- **URL**: `https://your-app-name.koyeb.app`
- **Admin**: `https://your-app-name.koyeb.app/admin`
- **Health**: `https://your-app-name.koyeb.app/health/`

### Next Steps:

1. ✅ Test login/logout
2. ✅ Create customer account
3. ✅ Submit service request
4. ✅ Configure Google Maps API key
5. ✅ Add technicians via admin
6. ✅ Run assignments

## Quick Reference

### Your Koyeb App URLs:
- Dashboard: https://app.koyeb.com/
- Your App: `https://your-app-name.koyeb.app`
- Logs: Dashboard → Your App → Logs
- Shell: Dashboard → Your App → Exec

### Important Files on GitHub:
- `production_data.json` - Your local database export
- `Dockerfile` - Production build configuration
- `requirements.txt` - Python dependencies
- `tech_routing/production_settings.py` - Production Django settings

## Success Checklist

- [ ] SECRET_KEY generated
- [ ] Koyeb account created
- [ ] GitHub connected to Koyeb
- [ ] App deployed
- [ ] PostgreSQL added
- [ ] Environment variables set
- [ ] Build successful
- [ ] App running
- [ ] Data imported (optional)
- [ ] Google Maps configured
- [ ] Can log in

## You're Done! 🚀

Your Django Tech Routing app is now live on Koyeb!

