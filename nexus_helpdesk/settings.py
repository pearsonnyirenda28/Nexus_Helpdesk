"""
NexusDesk - IT Help Desk & VoIP Tracking System
Django Settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# BASE CONFIGURATION
# ─────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env locally.
# On Vercel, environment variables are provided by Vercel dashboard / integrations.
load_dotenv(BASE_DIR / '.env')


# ─────────────────────────────────────────────
# SECURITY
# ─────────────────────────────────────────────

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-change-this-key'
)

DEBUG = os.environ.get(
    'DEBUG',
    'False'
).lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        'ALLOWED_HOSTS',
        '.vercel.app,localhost,127.0.0.1'
    ).split(',')
    if host.strip()
]


# ─────────────────────────────────────────────
# APPLICATIONS
# ─────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third-party
    'widget_tweaks',

    # Local apps
    'accounts',
    'helpdesk',
    'voip',
]


# ─────────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────────

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise for static asset serving on Vercel
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'helpdesk.middleware.AuditMiddleware',
]


# ─────────────────────────────────────────────
# URL / WSGI
# ─────────────────────────────────────────────

ROOT_URLCONF = 'nexus_helpdesk.urls'

WSGI_APPLICATION = 'nexus_helpdesk.wsgi.application'


# ─────────────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────

# Automatically switch to Postgres if running on Vercel with Neon or explicit DB_ENGINE variable
is_postgres_env = 'POSTGRES_HOST' in os.environ or os.environ.get('DB_ENGINE') == 'django.db.backends.postgresql'

DB_ENGINE = os.environ.get(
    'DB_ENGINE',
    'django.db.backends.postgresql' if is_postgres_env else 'django.db.backends.sqlite3'
)

if DB_ENGINE == 'django.db.backends.postgresql':

    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            # Checks Vercel Neon auto-created keys first, then custom DB_* keys
            'NAME': os.environ.get('POSTGRES_DATABASE') or os.environ.get('DB_NAME', 'nexusdesk'),
            'USER': os.environ.get('POSTGRES_USER') or os.environ.get('DB_USER', 'nexusdesk_user'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD') or os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('POSTGRES_HOST') or os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'OPTIONS': {
                'sslmode': 'require',  # Required for Neon Serverless Postgres
            },
        }
    }

else:

    # SQLite is for local development only.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'nexusdesk.db',
        }
    }


# ─────────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator'
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator'
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator'
    },
]


# ─────────────────────────────────────────────
# INTERNATIONALIZATION
# ─────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.environ.get(
    'TIME_ZONE',
    'Africa/Harare'
)

USE_I18N = True
USE_TZ = True


# ─────────────────────────────────────────────
# STATIC FILES
# ─────────────────────────────────────────────

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise storage engine for compressed static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ─────────────────────────────────────────────
# MEDIA FILES
# ─────────────────────────────────────────────

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# ─────────────────────────────────────────────
# DEFAULT PRIMARY KEY
# ─────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ─────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────

AUTH_USER_MODEL = 'auth.User'

LOGIN_URL = '/accounts/login/'

LOGIN_REDIRECT_URL = '/dashboard/'

LOGOUT_REDIRECT_URL = '/accounts/login/'


# ─────────────────────────────────────────────
# EMAIL
# ─────────────────────────────────────────────

EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)

EMAIL_HOST = os.environ.get(
    'EMAIL_HOST',
    ''
)

EMAIL_PORT = int(
    os.environ.get(
        'EMAIL_PORT',
        '587'
    )
)

EMAIL_USE_TLS = os.environ.get(
    'EMAIL_USE_TLS',
    'True'
).lower() in ('true', '1', 'yes')

EMAIL_HOST_USER = os.environ.get(
    'EMAIL_HOST_USER',
    ''
)

EMAIL_HOST_PASSWORD = os.environ.get(
    'EMAIL_HOST_PASSWORD',
    ''
)


# ─────────────────────────────────────────────
# SESSION
# ─────────────────────────────────────────────

SESSION_COOKIE_AGE = 28800

SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# ─────────────────────────────────────────────
# VOIP SETTINGS
# ─────────────────────────────────────────────

VOIP_DEFAULT_EXTENSION_LENGTH = 4

VOIP_CALL_TIMEOUT_MINUTES = 60