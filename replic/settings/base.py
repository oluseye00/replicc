"""
Django settings for RepliC project.
"""
import os
from pathlib import Path
from decouple import config
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Security Settings
SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here-change-in-production')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '.railway.app',  # Railway subdomain (keep for compatibility)
    '.onrender.com', # Render subdomain
    'replic.com',     # Your custom domain (if you have one)
]

# Allow iframe embedding for mobile simulator (development only)
X_FRAME_OPTIONS = 'ALLOWALL'

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'corsheaders',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'drf_spectacular',
    'django_extensions',
]

LOCAL_APPS = [
    'accounts',
    'content_generation',
    'video_matching',
    # 'payments',  # Not yet implemented
    # 'analytics',  # Not yet implemented
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'replic.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'replic.wsgi.application'

# Database
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    # Parse DATABASE_URL properly
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
    
    # Use production Supabase URL if available
    SUPABASE_DATABASE_URL = config('SUPABASE_DATABASE_URL', default=None)
    if SUPABASE_DATABASE_URL and not DEBUG:
        DATABASES['default'] = dj_database_url.parse(SUPABASE_DATABASE_URL)
else:
    # Check if we should use SQLite for local development
    DB_ENGINE = config('DB_ENGINE', default='django.db.backends.postgresql')
    
    if DB_ENGINE == 'django.db.backends.sqlite3':
        # SQLite configuration for local development
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / config('DB_NAME', default='db.sqlite3'),
            }
        }
    else:
        # Fallback to PostgreSQL config
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': config('DB_NAME', default='replic_db'),
                'USER': config('DB_USER', default='postgres'),
                'PASSWORD': config('DB_PASSWORD', default='postgres'),
                'HOST': config('DB_HOST', default='localhost'),
                'PORT': config('DB_PORT', default='5432'),
            }
        }

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Configuration
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://replic.com",  # Add your production domain
]

CORS_ALLOW_CREDENTIALS = True

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'RepliC API',
    'DESCRIPTION': 'Content creation platform with AI and video matching',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/',
}

# Celery Configuration (for async tasks)  
REDIS_URL = config('REDIS_URL', default=None)

# Only configure Celery if Redis URL is available
if REDIS_URL:
    # Simple Redis configuration for Upstash
    CELERY_BROKER_URL = REDIS_URL.replace('redis://', 'rediss://') if 'upstash.io' in REDIS_URL else REDIS_URL
    CELERY_RESULT_BACKEND = CELERY_BROKER_URL
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_TASK_SERIALIZER = 'json' 
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = TIME_ZONE

    # Redis SSL configuration for Upstash
    if 'upstash.io' in REDIS_URL:
        CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
        CELERY_BROKER_USE_SSL = True
else:
    # Disable Celery when no Redis is available
    CELERY_TASK_ALWAYS_EAGER = True

# AI API Keys
ANTHROPIC_API_KEY = config('ANTHROPIC_API_KEY', default='')
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Django Sites Framework
SITE_ID = 1

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Video Processing Settings
VIDEO_UPLOAD_PATH = 'uploads/videos/'
VIDEO_PROCESSED_PATH = 'processed/videos/'
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.mov', '.avi', '.mkv']

# Content Generation Settings
MAX_CONTENT_GENERATIONS_FREE = 10
MAX_CONTENT_GENERATIONS_STARTER = 100
MAX_CONTENT_GENERATIONS_CREATOR = 500
MAX_CONTENT_GENERATIONS_TEAM = 2000

# Development Settings
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    INTERNAL_IPS = ['127.0.0.1']

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'replic.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}