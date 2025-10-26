"""
PythonAnywhere-specific settings
This file contains settings that override the main settings.py for PythonAnywhere deployment.
"""

import os

# Detect if we're running on PythonAnywhere
ON_PYTHONANYWHERE = 'PYTHONANYWHERE' in os.environ

if ON_PYTHONANYWHERE:
    # Security settings
    DEBUG = False
    ALLOWED_HOSTS = [
        'yourusername.pythonanywhere.com',  # Replace 'yourusername' with your actual PythonAnywhere username
    ]
    
    # Add your PythonAnywhere domain here
    # You can add multiple domains:
    # ALLOWED_HOSTS = ['yourusername.pythonanywhere.com', 'yourcustomdomain.com']
    
    # Database configuration - SQLite is fine for PythonAnywhere free accounts
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db.sqlite3'),
        }
    }
    
    # Static files - PythonAnywhere will handle this
    STATIC_URL = '/static/'
    STATIC_ROOT = '/home/yourusername/tech_routing/static'  # Update 'yourusername'
    
    # Media files
    MEDIA_URL = '/media/'
    MEDIA_ROOT = '/home/yourusername/tech_routing/media'  # Update 'yourusername'
    
    # You can also store media files outside the project:
    # MEDIA_ROOT = '/home/yourusername/media'
    
    # Email settings (optional, for notifications)
    # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # EMAIL_HOST = 'smtp.gmail.com'
    # EMAIL_PORT = 587
    # EMAIL_USE_TLS = True
    # EMAIL_HOST_USER = 'your-email@gmail.com'
    # EMAIL_HOST_PASSWORD = 'your-app-password'
    
    # Logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': '/home/yourusername/tech_routing/logs/django.log',  # Create logs/ directory
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }
    
else:
    # Local development settings
    DEBUG = True
    ALLOWED_HOSTS = ['*']


