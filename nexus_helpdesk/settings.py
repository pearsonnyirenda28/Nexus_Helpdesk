"""
BeitDesk - Municipality of Beitbridge IT Help Desk & VoIP Tracking System
Django Settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'beitdesk-change-this-in-production-use-env-vars')

DEBUG = False

ALLOWED_HOSTS = ['*']

# ── Multi-device / LAN access ─────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    # Add your LAN IP here, e.g. 'http://192.168.1.50:8000',
]

SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'widget_tweaks',
    'accounts',
    'helpdesk.apps.HelpdeskConfig',
    'voip',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',          # <-- Whitenoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'helpdesk.db_router.YearDatabaseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'helpdesk.middleware.AuditMiddleware',
]

DATABASE_ROUTERS = ['helpdesk.db_router.YearDatabaseRouter']

ROOT_URLCONF = 'nexus_helpdesk.urls'

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
                'helpdesk.context_processors.global_stats',
            ],
        },
    },
]

WSGI_APPLICATION = 'nexus_helpdesk.wsgi.application'

# ── Helper to strip quotes from environment variables ──────────────────────
def strip_quotes(value):
    """Remove leading/trailing single or double quotes from a string."""
    if isinstance(value, str):
        value = value.strip()
        if (value.startswith("'") and value.endswith("'")) or \
           (value.startswith('"') and value.endswith('"')):
            return value[1:-1]
    return value

# ── Database ──────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': strip_quotes(os.environ.get('DB_NAME', 'neondb')),
        'USER': strip_quotes(os.environ.get('DB_USER', 'neondb_owner')),
        'PASSWORD': strip_quotes(os.environ.get('DB_PASSWORD')),
        'HOST': strip_quotes(os.environ.get('DB_HOST', 'ep-bitter-tooth-awd1rg7u-pooler.c-12.us-east-1.aws.neon.tech')),
        'PORT': strip_quotes(os.environ.get('DB_PORT', '5432')),
        'OPTIONS': {'sslmode': 'require'},
    }
}

# ── Password validation ──────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Harare'
USE_I18N = True
USE_TZ = True

# ── Static files (Whitenoise) ──────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'auth.User'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SESSION_COOKIE_AGE = 28800  # 8 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

VOIP_DEFAULT_EXTENSION_LENGTH = 4
VOIP_CALL_TIMEOUT_MINUTES = 60