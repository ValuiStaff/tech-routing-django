"""
Production settings for Django deployment on Koyeb/Cloud platforms
"""
import os
from .settings import *

# Security settings for production
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Allow all hosts
ALLOWED_HOSTS = ['*']

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Parse DATABASE_URL format: postgres://user:pass@host:port/dbname
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        result = urlparse(DATABASE_URL)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': result.path[1:],  # Remove leading /
                'USER': result.username,
                'PASSWORD': result.password,
                'HOST': result.hostname,
                'PORT': result.port or 5432,
                'CONN_MAX_AGE': 600,
                'OPTIONS': {
                    'connect_timeout': 10,
                }
            }
        }
    except Exception as e:
        print(f"Error parsing DATABASE_URL: {e}")
        # Fallback to SQLite if DATABASE_URL is invalid
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    # Default to SQLite if no DATABASE_URL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Add WhiteNoise for static files serving
MIDDLEWARE = MIDDLEWARE + ['whitenoise.middleware.WhiteNoiseMiddleware']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings (disable if behind proxy)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Google Maps API key
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
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
    },
}

# Time zone
USE_TZ = True
TIME_ZONE = 'Australia/Melbourne'

# Session configuration
SESSION_COOKIE_AGE = 86400
SESSION_COOKIE_HTTPONLY = True

# CSRF configuration
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Additional settings
USE_I18N = True
USE_L10N = True
