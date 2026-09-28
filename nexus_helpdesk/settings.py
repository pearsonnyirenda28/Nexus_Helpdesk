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

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = ['*']

# ── Multi-device / LAN / Deployment access ─────────────────────────────────────
# NOTE: Django does NOT support wildcards like 'https://*.vercel.app' in
# CSRF_TRUSTED_ORIGINS. Only exact origins count. Add your real deployment
# domains below (one per line), no scheme wildcards.
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://beit-desk.vercel.app',
    # Preview deployment pattern (Vercel gives each preview a unique subdomain).
    # Add the specific preview URL you're testing if you need CSRF to work there:
    # 'https://beit-desk-exgqrwp76-pearsonnyirenda28s-projects.vercel.app',
]

# ── Security & HTTPS Enforcement (Required for WebCam / getUserMedia) ─────────
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True

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
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ── Year database middleware DISABLED ──
    # It was injecting SQLite connections at request time, which fails on
    # Vercel's read-only filesystem. Re-enable only after refactoring to
    # Postgres schemas (see notes at bottom of file).
    # 'helpdesk.db_router.YearDatabaseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'helpdesk.middleware.AuditMiddleware',
]

# ── Year database router DISABLED ──
# See notes at bottom of file for how to reinstate year separation correctly.
DATABASE_ROUTERS = []

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

# ── Database (Neon PostgreSQL) ───────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': strip_quotes(os.environ.get('DB_NAME', 'neondb')),
        'USER': strip_quotes(os.environ.get('DB_USER', 'neondb_owner')),
        'PASSWORD': strip_quotes(os.environ.get('DB_PASSWORD')),
        'HOST': strip_quotes(os.environ.get(
            'DB_HOST',
            'ep-divine-frost-awqtvxaj-pooler.c-12.us-east-1.aws.neon.tech'
        )),
        'PORT': strip_quotes(os.environ.get('DB_PORT', '5432')),
        'OPTIONS': {'sslmode': 'require'},
        'CONN_MAX_AGE': 0,   # serverless functions should not reuse connections
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

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

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


# ────────────────────────────────────────────────────────────────────────────
# NOTES — restoring per-year databases later (do NOT re-enable SQLite on Vercel)
# ────────────────────────────────────────────────────────────────────────────
# Vercel's serverless filesystem is read-only outside /tmp, and /tmp is wiped
# on every cold start. SQLite cannot be used there.
#
# To restore the "Database Year" feature, use Postgres schemas in the SAME
# Neon database instead of separate SQLite files:
#
#   1. Create schemas:  CREATE SCHEMA year_2024; CREATE SCHEMA year_2025;
#   2. Middleware sets the search path per request:
#
#          from django.db import connection
#
#          class YearDatabaseMiddleware:
#              def __init__(self, get_response):
#                  self.get_response = get_response
#
#              def __call__(self, request):
#                  year = request.session.get('db_year')
#                  if year:
#                      with connection.cursor() as cur:
#                          cur.execute(f'SET search_path TO year_{year}, public')
#                  return self.get_response(request)
#
#   3. Router always returns 'default' (all data lives in the same DB).
#   4. Run migrations once per schema.
#
# Only after that refactor should YearDatabaseMiddleware be re-added to
# MIDDLEWARE and YearDatabaseRouter re-added to DATABASE_ROUTERS.
# ────────────────────────────────────────────────────────────────────────────