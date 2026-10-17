"""
Django settings for the Asante Church International website.

Secrets and settings that differ between your laptop and the live website
come from the .env file. Never write real secrets in this file.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Read the .env file in the project root (if it exists).
load_dotenv(BASE_DIR / '.env')


def env_bool(name, default=False):
    """Read a True/False value from the environment."""
    return os.environ.get(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


def env_list(name, default=''):
    """Read a comma-separated list from the environment."""
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]


# ---------------------------------------------------------------------------
# Core security settings
# ---------------------------------------------------------------------------

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY is missing. Add it to your .env file (see .env.example)."
    )

# Safe default: DEBUG is OFF unless the .env file turns it on.
DEBUG = env_bool('DJANGO_DEBUG', False)

# Only these website addresses are allowed to be served.
ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost')

# Needed once the site has a real https:// address (set in .env on the live site).
CSRF_TRUSTED_ORIGINS = env_list('DJANGO_CSRF_TRUSTED_ORIGINS')

# Extra protections that only switch on for the live site (DJANGO_HTTPS=True).
# They must stay off on your laptop, which uses plain http://127.0.0.1.
if env_bool('DJANGO_HTTPS', False):
    SESSION_COOKIE_SECURE = True     # login cookie only travels over https
    CSRF_COOKIE_SECURE = True        # form-protection cookie only travels over https
    SECURE_HSTS_SECONDS = 3600       # browsers remember "https only" (raised once everything is confirmed working)

# Switch these on ONLY on the live site, once https:// is confirmed working.
if env_bool('DJANGO_SSL_REDIRECT', False):
    SECURE_SSL_REDIRECT = True       # send http:// visitors to https://

if env_bool('DJANGO_PROXY_SSL_HEADER', False):
    # Only for hosts that put a proxy in front of Django and pass this header along.
    # Your host will tell you if you need this.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Always on (these are also Django's defaults; written here so they are visible)
SESSION_COOKIE_HTTPONLY = True       # JavaScript cannot read the login cookie
X_FRAME_OPTIONS = 'DENY'             # other sites cannot embed ours in a hidden frame
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'church',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'church.context_processors.church_globals',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ---------------------------------------------------------------------------
# Database (SQLite for now; PostgreSQL can be added later if the host offers it)
# ---------------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------------------------
# Language and time
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Kampala'
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Static files (CSS, JavaScript) and media files (uploaded photos)
# ---------------------------------------------------------------------------

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
# Where "python manage.py collectstatic" gathers every CSS/JS file for the live site.
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ---------------------------------------------------------------------------
# Email (Django 6.1 uses the MAILERS setting)
#
# On your laptop, emails are only PRINTED in the terminal window.
# On the live site, fill in the DJANGO_EMAIL_* values in .env to send real email.
# ---------------------------------------------------------------------------

if os.environ.get('DJANGO_EMAIL_HOST'):
    MAILERS = {
        'default': {
            'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'OPTIONS': {
                'host': os.environ['DJANGO_EMAIL_HOST'],
                'port': int(os.environ.get('DJANGO_EMAIL_PORT') or 587),
                'username': os.environ.get('DJANGO_EMAIL_HOST_USER', ''),
                'password': os.environ.get('DJANGO_EMAIL_HOST_PASSWORD', ''),
                'use_tls': env_bool('DJANGO_EMAIL_USE_TLS', True),
            },
        }
    }
else:
    MAILERS = {
        'default': {
            'BACKEND': 'django.core.mail.backends.console.EmailBackend',
        }
    }

DEFAULT_FROM_EMAIL = (
    os.environ.get('DJANGO_DEFAULT_FROM_EMAIL') or 'Asante Church Website <webmaster@localhost>'
)

# The church address that receives contact-form messages. Leave empty to turn this off.
CONTACT_NOTIFY_EMAIL = os.environ.get('DJANGO_CONTACT_NOTIFY_EMAIL', '')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'