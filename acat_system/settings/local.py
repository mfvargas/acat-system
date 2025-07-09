"""
Local development settings using PostgreSQL
"""

from .base import *
from decouple import config

# Use PostgreSQL for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': config('DB_NAME', default='acat_system_dev'),
        'USER': config('DB_USER', default='acat_user'),
        'PASSWORD': config('DB_PASSWORD', default='dev_password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Override specific settings for local development
DEBUG = True
ALLOWED_HOSTS = ['*']

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Add development tools
INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
]

# Debug toolbar middleware
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug toolbar configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# CORS for development
CORS_ALLOW_ALL_ORIGINS = True
