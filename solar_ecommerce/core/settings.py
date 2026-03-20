import os
from pathlib import Path
from datetime import timedelta


def env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).lower() in {'1', 'true', 'yes', 'on'}


def env_list(name: str, default: str = '') -> list[str]:
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]


BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = env_bool('DJANGO_DEBUG', False)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-dev-only-key-do-not-use-in-production'
    else:
        raise RuntimeError('DJANGO_SECRET_KEY environment variable is required in production.')


if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS')

    
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')

# ──────────────────────────────────────────────
# Application definition
# ──────────────────────────────────────────────

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.users',
    'apps.products',
    'apps.orders',
    'apps.reviews',
    'apps.wishlists',
    'apps.coupons',
    'apps.contacts',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # must be first to add CORS headers early
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'apps.middleware.InputSanitizationMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.middleware.SecurityHeadersMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ──────────────────────────────────────────────
# Database
# ──────────────────────────────────────────────

# Keep SQLite as the default database for simple Docker deployment.
# Switch to PostgreSQL by setting USE_POSTGRES=true or DB_HOST.
if env_bool('USE_POSTGRES', False) or os.environ.get('DB_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'solar_db'),
            'USER': os.environ.get('DB_USER', 'solar_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'db'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.environ.get('SQLITE_PATH', str(BASE_DIR / 'db.sqlite3')),
        }
    }

# ──────────────────────────────────────────────
# Auth
# ──────────────────────────────────────────────

AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ──────────────────────────────────────────────
# Internationalization
# ──────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────────
# Static & Media
# ──────────────────────────────────────────────

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# ──────────────────────────────────────────────
# Django REST Framework
# ──────────────────────────────────────────────

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/minute',
        'user': '120/minute',
        'auth': '5/minute',       # login / register
        'contact': '3/minute',    # contact form / newsletter
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'apps.exceptions.custom_exception_handler',
    # JSON-only in production (no Browsable API to prevent info leakage)
    'DEFAULT_RENDERER_CLASSES': (
        ['rest_framework.renderers.JSONRenderer', 'rest_framework.renderers.BrowsableAPIRenderer']
        if DEBUG else ['rest_framework.renderers.JSONRenderer']
    ),
}

# ──────────────────────────────────────────────
# API Documentation (drf-spectacular)
# ──────────────────────────────────────────────

SPECTACULAR_SETTINGS = {
    'TITLE': 'Solar E-Commerce API',
    'DESCRIPTION': 'Professional REST API for solar energy products e-commerce platform.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
}

# ──────────────────────────────────────────────
# Simple JWT
# ──────────────────────────────────────────────

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ──────────────────────────────────────────────
# CORS  (Next.js frontend)
# ──────────────────────────────────────────────

# In development allow all origins to simplify local frontend + backend setup.
# In production override via environment variable `CORS_ALLOWED_ORIGINS`.
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
else:
    # Allow origins provided via env var, otherwise fall back to Droplet frontend origin
    CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS') or [
        "http://138.197.11.80",
    ]
    CORS_ALLOW_CREDENTIALS = True

# ──────────────────────────────────────────────
# Default primary key field type
# ──────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ──────────────────────────────────────────────
# Security Hardening
# ──────────────────────────────────────────────

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

if not DEBUG:
    # HTTPS / HSTS
    SECURE_SSL_REDIRECT = env_bool('DJANGO_SECURE_SSL_REDIRECT', False)
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_SECURE_HSTS_SECONDS', '0'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
    SECURE_HSTS_PRELOAD = SECURE_HSTS_SECONDS > 0

    # Cookies
    secure_cookies = env_bool('DJANGO_SECURE_COOKIES', SECURE_SSL_REDIRECT)
    SESSION_COOKIE_SECURE = secure_cookies
    CSRF_COOKIE_SECURE = secure_cookies
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True

    # Headers
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
else:
    # Dev-friendly defaults
    X_FRAME_OPTIONS = 'SAMEORIGIN'
    SESSION_COOKIE_HTTPONLY = True

# ──────────────────────────────────────────────
# File Upload Limits
# ──────────────────────────────────────────────

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB

# Custom: max sizes for images & documents (validated in serializers)
MAX_IMAGE_UPLOAD_SIZE = 5 * 1024 * 1024           # 5 MB
MAX_DOCUMENT_UPLOAD_SIZE = 10 * 1024 * 1024        # 10 MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
ALLOWED_DOCUMENT_TYPES = ['application/pdf']