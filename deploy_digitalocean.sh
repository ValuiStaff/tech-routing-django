#!/bin/bash
# DigitalOcean Deployment Script for Django Tech Routing App
# This script helps deploy your Django app to DigitalOcean Droplet

set -e

echo "=========================================="
echo "DigitalOcean Deployment Script"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker not found!"
    echo "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✓ Docker found: $(docker --version)"
echo ""

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    if ! docker compose version &> /dev/null; then
        echo "Error: Docker Compose not found!"
        exit 1
    else
        COMPOSE_CMD="docker compose"
    fi
else
    COMPOSE_CMD="docker-compose"
fi

echo "✓ Docker Compose found"
echo ""

# Ask user for deployment option
echo "Deployment Options:"
echo "  1) Test locally first"
echo "  2) Deploy to existing DigitalOcean Droplet"
echo "  3) Show deployment instructions"
echo ""
read -p "Select option (1-3): " deploy_option

case $deploy_option in
    1)
        echo ""
        echo "Building and starting containers..."
        $COMPOSE_CMD up --build -d
        
        echo ""
        echo "✓ Containers started!"
        echo ""
        echo "Running migrations..."
        $COMPOSE_CMD exec web python manage.py migrate
        
        echo ""
        echo "Creating superuser (optional)..."
        $COMPOSE_CMD exec web python manage.py createsuperuser || true
        
        echo ""
        echo "=========================================="
        echo "✓ Application is running!"
        echo "=========================================="
        echo ""
        echo "Visit: http://localhost:8000"
        echo "Admin: http://localhost:8000/admin/"
        echo ""
        echo "View logs: docker-compose logs -f"
        echo "Stop: docker-compose down"
        echo ""
        ;;
    2)
        echo ""
        read -p "Enter Droplet IP address: " DROPLET_IP
        read -p "Enter SSH username (usually 'root'): " SSH_USER
        
        echo ""
        echo "Creating deployment package..."
        tar -czf django_deploy.tar.gz \
            --exclude='venv' \
            --exclude='*.pyc' \
            --exclude='__pycache__' \
            --exclude='.git' \
            --exclude='db.sqlite3' \
            --exclude='*.log' \
            docker-compose.yml Dockerfile .dockerignore tech_routing/ accounts/ core/ routing/ maps/ templates/ static/ requirements.txt
        
        echo ""
        echo "Uploading to DigitalOcean Droplet..."
        scp django_deploy.tar.gz docker-compose.yml deploy_digitalocean.sh $SSH_USER@$DROPLET_IP:~/
        
        echo ""
        echo "Running deployment on Droplet..."
        ssh $SSH_USER@$DROPLET_IP << 'ENDSSH'
cd ~/
tar -xzf django_deploy.tar.gz
docker-compose up --build -d
docker-compose exec web python manage.py migrate
echo "Deployment complete!"
ENDSSH
        
        echo ""
        echo "=========================================="
        echo "✓ Deployed to DigitalOcean!"
        echo "=========================================="
        echo "Visit: http://$DROPLET_IP:8000"
        echo ""
        ;;
    3)
        echo ""
        echo "=========================================="
        echo "DigitalOcean Deployment Instructions"
        echo "=========================================="
        echo ""
        echo "Option A: Deploy to New Droplet"
        echo "1. Create Droplet: https://cloud.digitalocean.com/droplets/new"
        echo "   - Choose Ubuntu 22.04"
        echo "   - Select size ($12/month minimum recommended)"
        echo "   - Enable SSH key or save root password"
        echo ""
        echo "2. Connect to Droplet:"
        echo "   ssh root@YOUR_DROPLET_IP"
        echo ""
        echo "3. Install Docker on Droplet:"
        echo "   curl -fsSL https://get.docker.com -o get-docker.sh"
        echo "   sh get-docker.sh"
        echo ""
        echo "4. Upload your project:"
        echo "   # From your local machine:"
        echo "   scp -r . root@YOUR_DROPLET_IP:/opt/django"
        echo ""
        echo "5. Deploy on Droplet:"
        echo "   cd /opt/django"
        echo "   docker-compose up --build -d"
        echo "   docker-compose exec web python manage.py migrate"
        echo ""
        echo "=========================================="
        echo ""
        echo "Option B: Deploy using App Platform (Easier)"
        echo "1. Go to: https://cloud.digitalocean.com/apps"
        echo "2. Click 'Create App'"
        echo "3. Connect GitHub repository"
        echo "4. Choose 'Docker' deployment"
        echo "5. Use docker-compose.yml we created"
        echo "6. Deploy automatically!"
        echo ""
        echo "=========================================="
        echo ""
        echo "Option C: Use DigitalOcean Spaces for Static Files"
        echo "1. Create Space: https://cloud.digitalocean.com/spaces"
        echo "2. Update settings.py to use Django-Storages"
        echo "3. Collect static files to Spaces"
        echo ""
        ;;
esac

