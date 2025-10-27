# Deploy with Local Data to Koyeb

## ✅ Data Export Complete!

Your local database has been exported to `production_data.json` and pushed to GitHub.

## Deploy Steps

### Step 1: Deploy to Koyeb
1. Go to https://app.koyeb.com/
2. Create App → Deploy from GitHub
3. Repository: `ValuiStaff/tech-routing-django`
4. Add PostgreSQL database
5. Set environment variables:
   ```bash
   DJANGO_SETTINGS_MODULE=tech_routing.production_settings
   DEBUG=False
   SECRET_KEY=<generate-this>
   GOOGLE_MAPS_API_KEY=<your-api-key>
   ```

### Step 2: Wait for Deployment
- Wait 5-10 minutes for build to complete
- App should be running

### Step 3: Import Your Data

Once deployed, access the Koyeb shell:

1. **Open App** in Koyeb dashboard
2. **Click "Exec"** or access terminal
3. Run these commands:

```bash
# Make sure you're in the app directory
cd /app

# Run migrations first
python manage.py migrate --noinput

# Import the data
python manage.py loaddata production_data.json
```

### Step 4: Create Superuser (if needed)

If you need to create a new superuser:

```bash
python manage.py createsuperuser
```

Or if your admin user is already in the exported data, you can log in with:
- Username from your local database
- Password from your local database

## What's Being Imported

The `production_data.json` file contains:
- ✅ User accounts (including your admin)
- ✅ Technicians
- ✅ Skills
- ✅ Service Requests
- ✅ Assignments
- ✅ Google Maps Config
- ✅ All app data

## Verify Data Import

1. Log into your Koyeb app
2. Check admin panel: `https://your-app.koyeb.app/admin`
3. Verify all data is present:
   - Users
   - Technicians
   - Skills
   - Service Requests
   - Google Maps Config

## Troubleshooting

### If import fails:
```bash
# Check for foreign key issues
python manage.py loaddata production_data.json --verbosity 2

# If content_type issues
python manage.py migrate --run-syncdb
```

### If password doesn't work:
- Local users keep their hashed passwords from SQLite
- If issues occur, create new superuser:
  ```bash
  python manage.py createsuperuser
  ```

### If you need to clear and reimport:
```bash
python manage.py flush --noinput
python manage.py migrate
python manage.py loaddata production_data.json
```

## Data Size

- File: `production_data.json`
- Size: ~23KB
- Contained: All your local data

## Alternative: Direct Shell Access

If you prefer using Koyeb's exec feature:

1. Go to your app in Koyeb
2. Click "Exec" button
3. Run the loaddata command in the shell
4. Done!

## What's Next

After importing data:
1. ✅ All your users are available
2. ✅ All technicians configured
3. ✅ All service requests present
4. ✅ Google Maps API config included
5. ✅ Start using your app!

## Important Notes

- **Passwords**: Local user passwords are preserved (hashed)
- **API Keys**: Google Maps API key is included in the export
- **Auto-Deploy**: Koyeb will automatically redeploy when you push to GitHub
- **Backup**: Keep your local `production_data.json` as a backup

## Quick Reference

```bash
# In Koyeb shell:
cd /app
python manage.py migrate
python manage.py loaddata production_data.json
python manage.py createsuperuser  # if needed
```

Your app is now ready with all local data! 🚀

