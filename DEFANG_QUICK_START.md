# Quick Start: Deploy to Defang.io

## Prerequisites

1. **Defang CLI installed**
```bash
# macOS
brew install defang/tap/defang

# Linux
curl -L https://github.com/DefangLabs/defang/releases/latest/download/defang-linux-x86_64.tar.gz -o defang.tar.gz
tar -xzf defang.tar.gz
sudo mv defang /usr/local/bin/
```

2. **Verify installation**
```bash
defang --version
```

## Option 1: Deploy to Defang Playground (Free, No Cloud Account Needed)

```bash
# Run the deployment script
./deploy_defang.sh

# Or manually:
defang compose up --playground
```

**That's it!** Your app will be live on Defang's playground.

## Option 2: Deploy to AWS

### Setup AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your region (e.g., us-east-1)
```

### Deploy
```bash
./deploy_defang.sh
# Select option 2 (AWS)

# Or manually:
defang compose up --platform aws
```

## Option 3: Deploy to GCP

### Setup GCP Credentials
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Deploy
```bash
./deploy_defang.sh
# Select option 3 (GCP)

# Or manually:
defang compose up --platform gcp
```

## Option 4: Deploy to DigitalOcean

### Setup DigitalOcean Token
```bash
export DIGITALOCEAN_ACCESS_TOKEN=your-token-here
```

### Deploy
```bash
./deploy_defang.sh
# Select option 4 (DigitalOcean)

# Or manually:
defang compose up --platform digitalocean
```

## Configure Environment Variables

Before deploying, set your secrets in Defang:

```bash
# Set secret key
defang secret set SECRET_KEY "your-secret-key-here"

# Set Google Maps API key
defang secret set GOOGLE_MAPS_API_KEY "your-api-key-here"

# Set database password
defang secret set DB_PASSWORD "secure-password-here"
```

Or edit `defang.toml` directly (not recommended for sensitive data).

## View Your App

After deployment:

1. Get your app URL:
```bash
defang status
```

2. Visit the URL in your browser!

## Common Commands

```bash
# Check status
defang status

# View logs
defang logs

# Restart services
defang compose restart

# Update application
defang compose up --update

# Stop deployment
defang compose down
```

## Troubleshooting

### Installation Issues
```bash
# Install Defang CLI
brew install defang/tap/defang
```

### Deployment Fails
```bash
# Check logs
defang logs

# Check status
defang status
```

### Can't Connect to Database
- Make sure `db` service is running
- Check environment variables in `defang.toml`

### Static Files Not Loading
- Run `python manage.py collectstatic` during build
- Check `STATIC_ROOT` in settings

## What's Included

Your deployment includes:

- **Web service**: Django application with Gunicorn
- **Database**: PostgreSQL 15
- **Redis**: For caching and sessions
- **Nginx**: For static file serving (optional)

## Custom Domain

If you have a paid Defang account:

```bash
defang domain add www.yourdomain.com
```

## Next Steps

1. Visit your app URL
2. Run migrations: Connect to database and run `python manage.py migrate`
3. Create superuser: Run `python manage.py createsuperuser`
4. Populate test data: Run `python manage.py populate_test_data`
5. Configure Google Maps API key in admin panel

## Production Checklist

- [ ] Set SECRET_KEY
- [ ] Set GOOGLE_MAPS_API_KEY
- [ ] Set DB_PASSWORD
- [ ] Run migrations
- [ ] Create superuser
- [ ] Test all features
- [ ] Monitor logs
- [ ] Set up custom domain (if needed)

## Support

- Defang Docs: https://docs.defang.io/
- Django Docs: https://docs.djangoproject.com/
- Check logs: `defang logs`

## Files Created

- `defang.toml` - Defang Compose configuration
- `Dockerfile` - Docker image configuration
- `.dockerignore` - Files to exclude from Docker build
- `tech_routing/production_settings.py` - Production settings
- `requirements.txt` - Updated with production dependencies
- `deploy_defang.sh` - Automated deployment script

**Ready to deploy? Run: `./deploy_defang.sh`** 🚀

