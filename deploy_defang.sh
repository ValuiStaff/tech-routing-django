#!/bin/bash
# Defang.io Deployment Script
# This script deploys your Django app to Defang.io

set -e

echo "======================================"
echo "Defang.io Deployment Script"
echo "======================================"
echo ""

# Check if Defang CLI is installed
if ! command -v defang &> /dev/null; then
    echo "Error: Defang CLI not found!"
    echo ""
    echo "Install Defang CLI:"
    echo "  macOS: brew install defang/tap/defang"
    echo "  Linux: See https://docs.defang.io/"
    exit 1
fi

echo "✓ Defang CLI found"
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found. Please run from Django project root."
    exit 1
fi

echo "✓ Project structure validated"
echo ""

# Check for required files
if [ ! -f "defang.toml" ]; then
    echo "Error: defang.toml not found!"
    echo "Please create defang.toml configuration file."
    exit 1
fi

if [ ! -f "Dockerfile" ]; then
    echo "Error: Dockerfile not found!"
    echo "Please create Dockerfile for your application."
    exit 1
fi

echo "✓ Required files found"
echo ""

# Ask user for deployment options
echo "Deployment Options:"
echo "  1) Deploy to Defang Playground (no cloud account needed)"
echo "  2) Deploy to AWS"
echo "  3) Deploy to GCP"
echo "  4) Deploy to DigitalOcean"
echo ""
read -p "Select option (1-4): " deploy_option

case $deploy_option in
    1)
        DEPLOY_ARGS="--playground"
        echo ""
        echo "Deploying to Defang Playground..."
        ;;
    2)
        DEPLOY_ARGS="--platform aws"
        echo ""
        echo "Deploying to AWS..."
        echo "Make sure AWS credentials are configured."
        ;;
    3)
        DEPLOY_ARGS="--platform gcp"
        echo ""
        echo "Deploying to GCP..."
        echo "Make sure GCP credentials are configured."
        ;;
    4)
        DEPLOY_ARGS="--platform digitalocean"
        echo ""
        echo "Deploying to DigitalOcean..."
        echo "Make sure DIGITALOCEAN_ACCESS_TOKEN is set."
        ;;
    *)
        echo "Invalid option. Exiting."
        exit 1
        ;;
esac

echo ""
echo "Starting deployment..."
echo ""

# Deploy with Defang
defang compose up $DEPLOY_ARGS

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✓ Deployment Successful!"
    echo "======================================"
    echo ""
    echo "Check deployment status:"
    echo "  defang status"
    echo ""
    echo "View logs:"
    echo "  defang logs"
    echo ""
    echo "Update application:"
    echo "  defang compose up $DEPLOY_ARGS --update"
    echo ""
else
    echo ""
    echo "======================================"
    echo "✗ Deployment Failed"
    echo "======================================"
    echo ""
    echo "Check logs for errors:"
    echo "  defang logs"
    echo ""
    echo "View error details in Defang dashboard"
    echo ""
    exit 1
fi

