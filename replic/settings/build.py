"""
Build-time settings for RepliC project.
Used during Docker build when DATABASE_URL is not available.
"""

from .base import *

# Build environment settings
DEBUG = False

# Use a dummy database for build-time operations like collectstatic
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Static files configuration
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Minimal settings needed for collectstatic
SECRET_KEY = 'build-time-secret-key-not-for-production'

# Disable features that require external services during build
CELERY_ALWAYS_EAGER = True
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable logging during build
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
}