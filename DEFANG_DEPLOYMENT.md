# Deploying Django App on Defang.io

Defang.io is an AI-powered DevOps platform that simplifies deployment to cloud platforms like AWS, GCP, and DigitalOcean.

## What You Need

1. **Defang CLI** installed on your machine
2. **Cloud Account** (AWS, GCP, or DigitalOcean) OR use Defang's Playground
3. **Docker** knowledge helpful but not required
4. Your Django project files

## Installation

### Install Defang CLI

**macOS:**
```bash
brew install defang/tap/defang
```

**Linux:**
```bash
curl -L https://github.com/DefangLabs/defang/releases/latest/download/defang-linux-x86_64.tar.gz -o defang.tar.gz
tar -xzf defang.tar.gz
sudo mv defang /usr/local/bin/
```

**Verify Installation:**
```bash
defang --version
```

## Create Defang Configuration

Create a `defang.toml` file in your project root:

```toml
# defang.toml
name = "tech-routing"

[services.web]
image = "python:3.10"
build = "."
ports = ["80:8000"]
environment = [
  "DJANGO_SECRET_KEY=your-secret-key-here",
  "GOOGLE_MAPS_API_KEY=your-api-key-here",
  "DATABASE_URL=postgresql://user:pass@db:5432/dbname"
]

[services.db]
image = "postgres:15"
environment = [
  "POSTGRES_DB=tech_routing",
  "POSTGRES_USER=django_user",
  "POSTGRES_PASSWORD=secure-password"
]

[services.static]
image = "nginx:alpine"
volumes = ["static:/static", "media:/media"]
```

## Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.10

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations
RUN python manage.py migrate

# Expose port
EXPOSE 8000

CMD ["gunicorn", "tech_routing.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Update Django Settings for Production

Create `tech_routing/production_settings.py`:

```python
from .settings import *
import os

DEBUG = False
ALLOWED_HOSTS = ['*']  # Update with your domain

# PostgreSQL database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'tech_routing'),
        'USER': os.environ.get('DB_USER', 'django_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files
STATIC_ROOT = '/static'
MEDIA_ROOT = '/media'

# Google Maps API Key
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
```

## Deploy to Defang Playground

**Deploy without cloud credentials:**
```bash
# Initialize project
defang init

# Deploy to Playground
defang compose up --playground
```

## Deploy to Cloud Platform

**For AWS:**
```bash
# Authenticate with AWS
aws configure

# Deploy
defang compose up --platform aws
```

**For GCP:**
```bash
# Authenticate with GCP
gcloud auth login

# Deploy
defang compose up --platform gcp
```

**For DigitalOcean:**
```bash
# Set DigitalOcean token
export DIGITALOCEAN_ACCESS_TOKEN=your-token

# Deploy
defang compose up --platform digitalocean
```

## Post-Deployment

### Get Your URL

```bash
defang status
```

### View Logs

```bash
defang logs
```

### Update Application

```bash
defang compose up --update
```

## Configuration Options

### Environment Variables

Set in `defang.toml`:
```toml
[services.web]
environment = [
  "DEBUG=False",
  "GOOGLE_MAPS_API_KEY=AIzaSy...",
]
```

### Custom Domain

```bash
defang domain add www.yourdomain.com
```

### Scaling

```toml
[services.web]
replicas = 3  # Run 3 instances
```

## Advantages of Defang

✓ Deploy to multiple cloud providers
✓ AI-powered debugging
✓ Automatic scaling
✓ Load balancing
✓ Managed databases (Postgres, MongoDB, Redis)
✓ Container orchestration
✓ CI/CD integration

## Disadvantages

✗ Requires Docker knowledge
✗ More complex than PythonAnywhere
✗ Needs cloud account (Playground is limited)
✗ CLI-based (no web interface)
✗ Learning curve for DevOps concepts

## Comparison: Defang vs PythonAnywhere

| Feature | Defang.io | PythonAnywhere |
|---------|-----------|----------------|
| Setup | Complex (CLI, Docker) | Simple (Web UI) |
| Scalability | High (cloud-native) | Limited (shared hosting) |
| Database | Postgres/NoSQL | SQLite (free) or MySQL |
| Custom Domain | Yes | Paid feature |
| Pricing | Pay for cloud resources | Free tier available |
| Automation | CI/CD built-in | Manual |
| Best For | Production apps, microservices | Learning, prototypes |
| Learning Curve | High | Low |
| Support | Community + AI | Community |

## Recommended Approach

**For your tech routing application:**

- **If you're learning:** PythonAnywhere (easier)
- **If you want production:** Defang + AWS/GCP (more powerful)
- **If you're on a budget:** PythonAnywhere (free tier)
- **If you need scaling:** Defang + cloud platform

## Next Steps

1. Choose: Defang or PythonAnywhere?
2. If Defang: Install CLI and set up cloud account
3. If PythonAnywhere: Follow PYTHONANYWHERE_DEPLOYMENT.md

## Documentation

- Defang Docs: https://docs.defang.io/
- Django on Defang: https://docs.defang.io/blog/2025/04/10/easiest-way-to-deploy-django
- Defang Website: https://defang.io/

