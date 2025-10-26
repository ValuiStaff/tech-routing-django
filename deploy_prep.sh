#!/bin/bash
# Deployment Preparation Script for PythonAnywhere
# This script prepares your Django project for deployment

echo "==================================="
echo "Django Deployment Preparation"
echo "==================================="
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found. Please run this script from the Django project root."
    exit 1
fi

echo "Step 1: Checking for sensitive data..."
if grep -q "django-insecure" tech_routing/settings.py; then
    echo "WARNING: Insecure SECRET_KEY found. Consider changing it for production."
fi

echo ""
echo "Step 2: Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "Step 3: Checking for migrations..."
python manage.py makemigrations --check --dry-run

echo ""
echo "Step 4: Creating deployment archive..."
# Create a zip file excluding unnecessary files
zip -r django_deployment.zip \
    . \
    -x "venv/*" \
    -x "*.pyc" \
    -x "__pycache__/*" \
    -x "*.log" \
    -x ".git/*" \
    -x "db.sqlite3" \
    -x ".env" \
    -x ".DS_Store"

echo ""
echo "==================================="
echo "Preparation Complete!"
echo "==================================="
echo ""
echo "Generated files:"
echo "  - django_deployment.zip (for upload to PythonAnywhere)"
echo ""
echo "Next steps:"
echo "1. Upload django_deployment.zip to PythonAnywhere"
echo "2. Extract in /home/yourusername/"
echo "3. Follow PYTHONANYWHERE_DEPLOYMENT.md guide"
echo ""
echo "IMPORTANT REMINDERS:"
echo "- Update 'yourusername' in pythonanywhere_settings.py"
echo "- Set Google Maps API key"
echo "- Run: python manage.py migrate"
echo "- Run: python manage.py collectstatic"
echo "- Configure web app in PythonAnywhere dashboard"
echo ""

