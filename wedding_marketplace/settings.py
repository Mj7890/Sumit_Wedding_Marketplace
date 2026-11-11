from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-change-this-in-production-abc123xyz'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cards',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # serves static files on PythonAnywhere
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wedding_marketplace.urls'

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
                'cards.context_processors.cart_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'wedding_marketplace.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# ── Email Configuration ──
EMAIL_BACKEND  = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Arts By Graphic <noreply@artsbygraphic.com>'

# ── Mailbuster API (free transactional email) ──────────────────────────────
# Sign up at https://mailbuster.io and get your API key
# Set these in your environment or replace the values below:
import os
MAILBUSTER_API_KEY    = os.environ.get('MAILBUSTER_API_KEY', '')
MAILBUSTER_FROM_EMAIL = os.environ.get('MAILBUSTER_FROM_EMAIL', 'noreply@artsbygraphic.com')
MAILBUSTER_FROM_NAME  = os.environ.get('MAILBUSTER_FROM_NAME',  'Arts By Graphic')
# ─────────────────────────────────────────────────────────────────────────────
# HOW TO SET ON PYTHONANYWHERE:
# 1. Go to PythonAnywhere → Files → open this settings.py
# 2. Replace MAILBUSTER_API_KEY = os.environ.get(..., '')
#    with  MAILBUSTER_API_KEY = 'your_actual_api_key_here'
# 3. Also set MAILBUSTER_FROM_EMAIL to a verified sender in your Mailbuster account
# 4. Reload your web app

# ── PythonAnywhere / Production CSRF fix ──
# Add your PythonAnywhere domain below
CSRF_TRUSTED_ORIGINS = [
    'https://*.pythonanywhere.com',
    'http://*.pythonanywhere.com',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Session security
SESSION_COOKIE_AGE       = 86400 * 7   # 7 days
SESSION_COOKIE_HTTPONLY  = True
SESSION_SAVE_EVERY_REQUEST = True

# ── WhiteNoise static file serving (PythonAnywhere / production) ──
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
