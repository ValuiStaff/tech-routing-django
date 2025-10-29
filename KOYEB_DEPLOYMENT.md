# Deploying Django Tech Routing App on Koyeb

## Prerequisites
- GitHub account with this repository
- Koyeb account (free tier available)
- Google Maps API key

## Step 1: Push to GitHub

```bash
git add .
git commit -m "Prepare for Koyeb deployment"
git push origin main
```

## Step 2: Create Koyeb App

1. Go to [Koyeb Dashboard](https://app.koyeb.com/)
2. Click **Create App**
3. Choose **GitHub** as the source
4. Authorize Koyeb to access your GitHub
5. Select your repository: `ValuiStaff/tech-routing-django`

## Step 3: Configure Build Settings

In the "Build & Deploy" section:

- **Build Command**: (leave default - Docker will handle this)
- **Dockerfile**: `Dockerfile`
- **Docker Context**: `.` (current directory)

## Step 4: Add Environment Variables

In the "Environment Variables" section, add:

```
DEBUG=False
SECRET_KEY=<generate-a-random-secret-key>
DJANGO_SETTINGS_MODULE=tech_routing.production_settings
GOOGLE_MAPS_API_KEY=<your-google-maps-api-key>

# Database (Koyeb will provide PostgreSQL automatically)
DATABASE_URL=<koyeb-postgres-url>

# Optional: Gunicorn settings
GUNICORN_WORKERS=3
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=120
```

### How to get SECRET_KEY:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Step 5: Add PostgreSQL Database

1. In your Koyeb app, go to **Data** tab
2. Click **Create Database**
3. Select **PostgreSQL**
4. Copy the `DATABASE_URL` from the database details
5. Add it to your app's environment variables

## Step 6: Deploy

1. Click **Deploy** in Koyeb
2. Wait for build to complete (5-10 minutes first time)
3. Once deployed, click **Open Application**

## Step 7: Run Initial Setup

After deployment, you need to create a superuser:

### Option A: Using Koyeb Web Console
1. Go to your app in Koyeb
2. Click **Console** tab
3. Run: `python manage.py createsuperuser`

### Option B: Using Koyeb CLI
```bash
koyeb run <your-app-name> python manage.py createsuperuser
```

## Step 8: Import Data (Optional)

To import your local data:

```bash
# Export data locally
python manage.py dumpdata > data.json

# Import on Koyeb
# Use Koyeb console or CLI
koyeb run <app-name> python manage.py loaddata data.json
```

## Important Notes

1. **Static Files**: Handled by WhiteNoise middleware automatically
2. **Media Files**: For production media storage, consider using:
   - AWS S3
   - Cloudinary
   - Google Cloud Storage
3. **Health Check**: App includes `/health/` endpoint for monitoring
4. **SSL**: Automatically handled by Koyeb
5. **Auto-deploy**: Every push to `main` branch triggers redeployment

## Troubleshooting

### Build fails
- Check Dockerfile is in root directory
- Verify requirements.txt is up to date
- Check build logs in Koyeb dashboard

### Database connection error
- Verify DATABASE_URL is correct
- Check database is running
- Wait a few minutes for database to fully provision

### Static files not loading
- Clear browser cache
- Check WhiteNoise is configured correctly
- Verify STATIC_ROOT is set

### 500 errors
- Check Koyeb logs for specific error
- Verify all environment variables are set
- Ensure SECRET_KEY is not placeholder

## Monitoring

- View logs in Koyeb dashboard under **Logs** tab
- Set up alerts in **Monitoring** section
- Track resource usage in **Metrics** tab

## Scaling

Koyeb automatically scales your app based on traffic. For manual scaling:
1. Go to **Scaling** tab
2. Adjust instance count
3. Save changes

## Next Steps

1. Set up custom domain in Koyeb
2. Enable monitoring and alerts
3. Configure backups for database
4. Set up CI/CD for automatic deployments
