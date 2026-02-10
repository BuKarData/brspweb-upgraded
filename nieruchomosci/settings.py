import os
from pathlib import Path
import dj_database_url

# Ścieżki
BASE_DIR = Path(__file__).resolve().parent.parent

#  Bezpieczny Secret Key
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "super-secret-key")

# Debug
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

# Dozwolone hosty
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",") if os.environ.get("ALLOWED_HOSTS") else [
    "braspol.pl",
    "www.braspol.pl",
    "*.up.railway.app",
    ".railway.app",
    "localhost",
    "127.0.0.1"
]

# Dla Railway - akceptuj wszystkie subdomeny
if os.environ.get("RAILWAY_ENVIRONMENT"):
    ALLOWED_HOSTS = ["*"]


# CSRF - dla Railway i produkcji
CSRF_TRUSTED_ORIGINS = [
    "https://www.braspol.pl",
    "https://braspol.pl",
]

# Dodaj Railway domeny jeśli na Railway
if os.environ.get("RAILWAY_ENVIRONMENT"):
    CSRF_TRUSTED_ORIGINS.extend([
        "https://*.up.railway.app",
        "https://*.railway.app",
    ])

# Bezpieczeństwo SSL - tylko na produkcji
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


# Aplikacje
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.humanize",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "oferty",
    "rest_framework",
]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # statyczne pliki
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    'django.middleware.locale.LocaleMiddleware',
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

#  URL conf i WSGI
ROOT_URLCONF = "nieruchomosci.urls"
WSGI_APPLICATION = "nieruchomosci.wsgi.application"

# Szablony
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# Database configuration - Railway automatycznie ustawi DATABASE_URL
database_url = (
    os.environ.get('DATABASE_URL')
    or os.environ.get('DATABASE_PUBLIC_URL')
    or os.environ.get('RAILWAY_DATABASE_URL')
    or os.environ.get('POSTGRES_URL')
)

if database_url:
    # Produkcja (Railway) - użyj DATABASE_URL
    DATABASES = {
        "default": dj_database_url.config(
            default=database_url,
            conn_max_age=600
        )
    }
else:
    # Lokalne środowisko - użyj SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Walidatory haseł
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

#  Międzynarodowe ustawienia
LANGUAGE_CODE = "pl"
TIME_ZONE = "Europe/Warsaw"
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = [
    ('pl', 'Polski'),

]

#  Pliki statyczne
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

#  Pliki media (jeżeli używasz)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

#  Domyślne auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"