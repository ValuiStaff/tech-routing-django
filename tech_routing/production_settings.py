"""
Production settings for Django deployment on Koyeb/Cloud platforms
This extends the base settings with production-specific configurations
"""

import os
from .settings import *

# Security settings for production
DEBUG = False

# Allow all hosts (Defang will handle domain routing)
ALLOWED_HOSTS = ['*']

# Database configuration - PostgreSQL
# Support both DATABASE_URL and individual variables
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Parse DATABASE_URL if provided
    import re
    db_match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
    if db_match:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': db_match.group(5),
                'USER': db_match.group(1),
                'PASSWORD': db_match.group(2),
                'HOST': db_match.group(3),
                'PORT': db_match.group(4),
                'CONN_MAX_AGE': 600,
            }
        }
    else:
        # Fallback to default
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'tech_routing',
                'USER': 'django_user',
                'PASSWORD': 'django_password',
                'HOST': 'db',
                'PORT': '5432',
                'CONN_MAX_AGE': 600,
            }
        }
else:
    # Use individual environment variables
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', os.environ.get('POSTGRES_DB', 'tech_routing')),
            'USER': os.environ.get('DB_USER', os.environ.get('POSTGRES_USER', 'django_user')),
            'PASSWORD': os.environ.get('DB_PASSWORD', os.environ.get('POSTGRES_PASSWORD', 'django_password')),
            'HOST': os.environ.get('DB_HOST', 'db'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'CONN_MAX_AGE': 600,
        }
    }

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = '/static'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = '/media'

# Security settings
SECURE_SSL_REDIRECT = True  # Defang handles HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Secret key from environment
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)

# Google Maps API key
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')

# Logging configuration (console only for Docker)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'tech_routing': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Cache configuration (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}

# Email configuration (optional)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

# Additional production settings
USE_TZ = True
TIME_ZONE = 'Australia/Melbourne'  # Or 'UTC'

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_AGE = 86400  # 1 day

# CSRF configuration
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

