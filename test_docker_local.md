# Test Docker Locally

## Build and Run with Docker Compose

```bash
cd "/Users/staffuser/Desktop/App Generation /django"
docker-compose up --build
```

This will:
1. Build the Django app container
2. Start PostgreSQL database
3. Start Redis
4. Run migrations automatically
5. Make your app available at http://localhost:8000

## Test with Koyeb Procfile

Or use the simpler Docker approach:

```bash
# Build
docker build -t tech-routing-local .

# Run with SQLite (simpler for testing)
docker run -p 8000:8000 \
  -e DJANGO_SETTINGS_MODULE=tech_routing.settings \
  -e SECRET_KEY=test-secret-key \
  -e GOOGLE_MAPS_API_KEY=AIzaSyCZCEanL50XqkGdej2VdZUCwRrkcf1RrYw \
  tech-routing-local
```

## What to Test

1. **Visit**: http://localhost:8000
2. **Admin**: http://localhost:8000/admin/
3. **Customer**: http://localhost:8000/core/customer/dashboard/
4. **Technician**: http://localhost:8000/core/technician/dashboard/

## After Local Testing Passes

Once Docker works locally, you can:
1. Push to GitHub
2. Deploy to Koyeb (Koyeb will use the same Dockerfile)
3. Your app will work the same way!

