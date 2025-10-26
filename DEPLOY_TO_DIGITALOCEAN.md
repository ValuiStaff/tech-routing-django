# Deploy to DigitalOcean App Platform - Simple Guide

## Quick Steps

### 1. Push to GitHub (If you haven't already)

Create a GitHub repository and push your code:

```bash
# Create repo on GitHub first, then:

git remote add origin https://github.com/YOUR_USERNAME/tech-routing-django.git
git branch -M main
git push -u origin main
```

Or use the GitHub Desktop app or GitHub web interface to create a repository and upload files.

### 2. Deploy to DigitalOcean

1. **Go to**: https://cloud.digitalocean.com/apps

2. **Click**: "Create App"

3. **Connect GitHub**: 
   - Select your repository
   - Or upload from GitHub manually

4. **Configure App**:
   - **Type**: Select "Docker"
   - **Build Command**: Leave empty (auto-detected)
   - **Run Command**: `gunicorn tech_routing.wsgi:application --bind 0.0.0.0:8080 --workers 2`
   - **Port**: `8080` (DigitalOcean auto-maps this)

5. **Resources** (Recommended):
   - **Basic Plan**: $5/month (512MB RAM) or $12/month (1GB RAM)
   - **Add Database**: PostgreSQL (recommended) - $15/month
   - **Or use**: SQLite (free, but less ideal for production)

6. **Environment Variables**:
   Add these in the App Settings:
   ```
   DJANGO_SETTINGS_MODULE=tech_routing.production_settings
   DEBUG=False
   SECRET_KEY=your-secret-key-here
   GOOGLE_MAPS_API_KEY=your-google-maps-key
   DATABASE_URL=${{do.postgres.DATABASE_URL}}
   ```

7. **Click**: "Create Resources" and wait for deployment

### 3. Configure Your App

Once deployed:

1. **Visit**: Your app URL (shown in DigitalOcean)

2. **Run migrations**:
   ```bash
   # In DigitalOcean console or via their shell:
   python manage.py migrate
   ```

3. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

4. **Populate test data** (optional):
   ```bash
   python manage.py populate_test_data
   ```

### 4. Access Your App

- **URL**: https://your-app-name.ondigitalocean.app
- **Admin**: https://your-app-name.ondigitalocean.app/admin/

## Important Notes

### Using docker-compose.yml

DigitalOcean App Platform **may not support docker-compose.yml directly**. If that's the case:

1. **Option A**: Use the Dockerfile directly (we created this!)
   - Builds your app automatically
   - No docker-compose.yml needed

2. **Option B**: Deploy to Droplet instead
   - Full Docker Compose support
   - More control
   - See `DIGITALOCEAN_DEPLOYMENT.md` for instructions

### Database Options

**Recommended: PostgreSQL**
- Add managed database in App Platform
- Update DATABASE_URL environment variable

**Simpler: SQLite**
- Works but not ideal for production
- Data lost if app restarts

## Troubleshooting

### App won't start
- Check logs in DigitalOcean dashboard
- Verify environment variables
- Check Dockerfile is correct

### Database errors
- Run migrations: `python manage.py migrate`
- Check DATABASE_URL is correct
- Use PostgreSQL for production

### Static files not loading
- Set STATIC_ROOT in settings
- Run: `python manage.py collectstatic --noinput`
- Configure static file serving in App Platform

### Google Maps not working
- Check API key is set correctly
- Enable these APIs in Google Cloud Console:
  - Maps JavaScript API
  - Places API
  - Geocoding API
  - Distance Matrix API

## Cost

**Basic Setup**: ~$5-20/month
- App: $5-12/month (512MB-1GB RAM)
- Database: $15/month (PostgreSQL)
- Total: ~$20-27/month

**With Discount Code**: Often $100-200 credit for new accounts!

## Next Steps After Deployment

1. ✅ Visit your app URL
2. ✅ Log in as admin
3. ✅ Run migrations
4. ✅ Create superuser
5. ✅ Configure Google Maps API key
6. ✅ Populate test data
7. ✅ Test all features

## Support

- DigitalOcean Docs: https://docs.digitalocean.com/products/app-platform/
- Django Docs: https://docs.djangoproject.com/
- Your app is ready to deploy! 🚀

