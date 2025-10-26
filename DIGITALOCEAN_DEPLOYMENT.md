# Deploy to DigitalOcean - Complete Guide

## What You Need

1. DigitalOcean account: https://cloud.digitalocean.com/
2. Your Django project (you have everything!)
3. Docker and Docker Compose

## Quick Start Options

### Option 1: Deploy to DigitalOcean App Platform (Easiest)

**Recommended for beginners!**

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Go to DigitalOcean App Platform**
   - Visit: https://cloud.digitalocean.com/apps
   - Click "Create App"
   - Connect your GitHub repository
   - Choose "Docker" as the app type
   - Select `docker-compose.yml`
   - DigitalOcean will auto-detect and deploy!

**That's it!** DigitalOcean handles everything.

### Option 2: Deploy to Droplet (More Control)

**Full server control:**

1. **Create a Droplet**
   - Go to: https://cloud.digitalocean.com/droplets/new
   - Choose: Ubuntu 22.04
   - Plan: $12/month (2GB RAM minimum)
   - Click "Create Droplet"

2. **SSH into Droplet**
   ```bash
   ssh root@YOUR_DROPLET_IP
   ```

3. **Install Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

4. **Upload Your Project**
   ```bash
   # From your local machine
   scp -r /Users/staffuser/Desktop/App\ Generation\ /django root@YOUR_DROPLET_IP:/opt/django
   ```

5. **Deploy on Droplet**
   ```bash
   ssh root@YOUR_DROPLET_IP
   cd /opt/django
   docker-compose up --build -d
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py collectstatic --noinput
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Access Your App**
   - Visit: http://YOUR_DROPLET_IP:8000
   - Admin: http://YOUR_DROPLET_IP:8000/admin/

### Option 3: Test Locally First

**Before deploying, test with Docker Compose:**

```bash
# Build and run
docker-compose up --build

# In another terminal, run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access at http://localhost:8000
```

## Automated Deployment Script

Use the script we created:

```bash
./deploy_digitalocean.sh
```

Select option 1 to test locally, or option 2 to deploy to a Droplet.

## Production Configuration

### Environment Variables

On your Droplet, create `.env` file:

```bash
# On DigitalOcean Droplet
nano /opt/django/.env
```

Add these variables:

```env
DEBUG=False
SECRET_KEY=your-super-secret-key-here
GOOGLE_MAPS_API_KEY=your-google-maps-key
DATABASE_URL=postgresql://user:password@db:5432/tech_routing
REDIS_URL=redis://redis:6379/0
```

### Configure Domain (Optional)

If you have a domain:

1. **Point DNS to your Droplet**
   - Add A record: `@` → YOUR_DROPLET_IP
   - Add A record: `www` → YOUR_DROPLET_IP

2. **Update ALLOWED_HOSTS**
   Edit `tech_routing/production_settings.py`:
   ```python
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'YOUR_DROPLET_IP']
   ```

3. **Use Nginx for HTTPS** (optional)
   ```bash
   sudo apt install nginx certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs web

# Check container status
docker-compose ps

# Restart containers
docker-compose restart
```

### Database Errors

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create database if missing
docker-compose exec web python manage.py dbinit
```

### Static Files Not Loading

```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check static volume
docker volume ls
```

### Google Maps Not Working

1. Check API key is set: `docker-compose exec web env | grep GOOGLE`
2. Enable these APIs in Google Cloud Console:
   - Maps JavaScript API
   - Places API
   - Geocoding API
   - Distance Matrix API

## Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
```

### Check Resource Usage

```bash
# Docker stats
docker stats

# Disk usage
df -h
```

### Backup Database

```bash
# Create backup
docker-compose exec db pg_dump -U django_user tech_routing > backup.sql

# Restore backup
docker-compose exec -T db psql -U django_user tech_routing < backup.sql
```

## Security Checklist

- [ ] `DEBUG = False` in production
- [ ] Strong SECRET_KEY
- [ ] ALLOWED_HOSTS configured
- [ ] HTTPS enabled (with certbot if using domain)
- [ ] Regular backups
- [ ] Firewall configured
- [ ] SSH key authentication
- [ ] Strong database passwords

## Scaling

### Add More Web Workers

Edit `docker-compose.yml`:

```yaml
services:
  web:
    deploy:
      replicas: 3
```

### Use Load Balancer

Create a DigitalOcean Load Balancer:
- Go to: https://cloud.digitalocean.com/networking/load-balancers
- Add your Droplets as targets
- Configure health checks

### Database Scaling

For production, use DigitalOcean Managed Database:
- Go to: https://cloud.digitalocean.com/databases
- Create PostgreSQL cluster
- Update `DATABASE_URL` in `.env`

## Cost Estimate

### Basic Setup
- Droplet ($12/month): 2GB RAM
- Free DigitalOcean spaces for static files
- Total: ~$12/month

### Production Setup
- Droplet ($24/month): 4GB RAM
- Managed Database ($15/month)
- Load Balancer ($12/month)
- Spaces for static ($5/month)
- Total: ~$56/month

## Next Steps After Deployment

1. Visit your app URL
2. Run migrations
3. Create superuser
4. Populate test data (optional)
5. Configure Google Maps API key
6. Test all features
7. Set up backups
8. Configure monitoring

## Support

- DigitalOcean Docs: https://docs.digitalocean.com/
- Docker Compose Docs: https://docs.docker.com/compose/
- Django Docs: https://docs.djangoproject.com/

## Your Files

All deployment files are ready:
- ✅ `docker-compose.yml` - Docker Compose configuration
- ✅ `Dockerfile` - Production-ready image
- ✅ `.dockerignore` - Exclude unnecessary files
- ✅ `tech_routing/production_settings.py` - Production settings
- ✅ `deploy_digitalocean.sh` - Deployment script

**Ready to deploy!** 🚀

