"""
Staging settings for ACAT System
"""

from .base import *

# Staging specific settings
DEBUG = config('DEBUG', default=False, cast=bool)

# Database - PostgreSQL with PostGIS for staging
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': config('DB_NAME', default='acat_system_staging'),
        'USER': config('DB_USER', default='acat_user'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

ALLOWED_HOSTS = [
    'staging.acatcr.org',
    'localhost',
    '127.0.0.1',
]

# CSRF and CORS for staging
CSRF_TRUSTED_ORIGINS = [
    'https://staging.acatcr.org',
]

CORS_ALLOWED_ORIGINS = [
    "https://staging.acatcr.org",
]

# Static files
STATIC_ROOT = '/var/www/acat-system/static/'
MEDIA_ROOT = '/var/www/acat-system/media/'

# Email backend for staging (console for testing)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Security - relaxed for staging
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Logging for staging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/acat-system/staging.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['file', 'console'],
    },
    'loggers': {
        'django': {
            'level': 'DEBUG',
            'handlers': ['file', 'console'],
            'propagate': False,
        },
    },
}
