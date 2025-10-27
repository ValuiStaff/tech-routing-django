# Django Tech Routing App - Production Dockerfile for Koyeb
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p staticfiles media logs

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=tech_routing.production_settings \
    PORT=8000

# Set SECRET_KEY for collectstatic (required)
ENV SECRET_KEY=temp-secret-key-for-collectstatic

# Collect static files - skip if it fails
RUN python manage.py collectstatic --noinput 2>/dev/null || echo "Static files collection failed, continuing..."

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health/ || exit 1

# Run migrations and start server
CMD python manage.py migrate --noinput && \
    gunicorn tech_routing.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${GUNICORN_WORKERS:-3} \
    --threads ${GUNICORN_THREADS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --log-level info
