# Deploy to Defang.io Using MCP

## What is Defang MCP?

Defang provides an MCP (Model Context Protocol) server that integrates with Cursor, allowing you to deploy applications through the IDE without installing additional CLIs.

## MCP Integration in Cursor

Your Cursor already has MCP support configured. You can interact with Defang through the MCP interface.

## How to Deploy Using Defang MCP

### Step 1: Use the Defang MCP Tools in Cursor

Cursor's MCP integration provides access to Defang tools. You can:

1. **Navigate your project** in Cursor
2. **Ask Cursor to deploy** using the Defang MCP server
3. **The MCP server** will handle the deployment process

### Step 2: Configure Defang Deployment

The MCP server can work with:

1. **defang.toml** - We've already created this!
2. **Dockerfile** - We've already created this!
3. **Production settings** - We've already created this!

### Step 3: Deploy Commands

Through Cursor's MCP interface, you can execute:

```
# Initialize Defang in your project
defang init

# Deploy to playground (free, no cloud account)
defang compose up --playground

# Or deploy to a cloud provider
defang compose up --platform aws
defang compose up --platform gcp
defang compose up --platform digitalocean
```

### Step 4: Environment Variables

Set your secrets through the MCP interface:

```
defang secret set SECRET_KEY "your-secret-key"
defang secret set GOOGLE_MAPS_API_KEY "your-api-key"
defang secret set DB_PASSWORD "secure-password"
```

## What We've Already Created

✅ **defang.toml** - Defang Compose configuration
✅ **Dockerfile** - Multi-stage production build
✅ **.dockerignore** - Files to exclude
✅ **tech_routing/production_settings.py** - Production settings
✅ **requirements.txt** - Updated with production deps
✅ **docker-compose.yml** - Alternative deployment option

## Deployment Workflow

1. **Cursor uses MCP** to communicate with Defang
2. **Defang MCP server** reads your `defang.toml`
3. **Builds and deploys** your Docker containers
4. **Provides URL** to access your app

## Alternative: If MCP Isn't Working

Since the MCP integration might not be fully set up, you can:

### Option A: Use Docker Compose Locally

The `docker-compose.yml` we created works anywhere:

```bash
# Build and run
docker-compose up --build

# Your app will be at http://localhost:8000
```

### Option B: Deploy to Cloud with Docker

1. **Upload your project** to a cloud platform
2. **Run Docker Compose** there:
   - AWS EC2
   - DigitalOcean Droplet
   - Railway
   - Render

### Option C: Use PythonAnywhere

Still the easiest option with all the files ready!

## Current Status

We have all the deployment files ready. The Defang MCP integration in Cursor should be able to use these files.

## Quick Test

Try asking Cursor:
- "Use Defang MCP to deploy this Django app"
- "Initialize Defang for this project"
- "Deploy to Defang Playground"

The MCP server should be able to use our prepared files!

