# Quick Deploy - Koyeb with Data

## 🚀 Your data is ready!

**Exported**: `production_data.json` (23KB)  
**GitHub**: Pushed to repository  
**Status**: Ready to deploy

## 3-Step Deployment

### 1. Deploy on Koyeb
- Go to https://app.koyeb.com/
- Create App → Deploy from GitHub
- Select: `ValuiStaff/tech-routing-django`
- **Add PostgreSQL** database
- Set environment variables
- Deploy!

### 2. Wait for Build
- 5-10 minutes for deployment
- App will be running

### 3. Import Data
Access Koyeb shell and run:

```bash
cd /app
python manage.py migrate
python manage.py loaddata production_data.json
```

## Environment Variables

```bash
DJANGO_SETTINGS_MODULE=tech_routing.production_settings
DEBUG=False
SECRET_KEY=<generate-this>
GOOGLE_MAPS_API_KEY=<your-key>
```

## What's Included

✅ User accounts  
✅ Technicians  
✅ Skills  
✅ Service requests  
✅ Assignments  
✅ Google Maps config  

## Done!

Your app is live with all local data! 🎉

## Full Guide

See: `DEPLOY_WITH_DATA.md`

