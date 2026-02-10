import os
from pathlib import Path
import dj_database_url

# Ścieżki
BASE_DIR = Path(__file__).resolve().parent.parent

#  Bezpieczny Secret Key
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "super-secret-key")

# Debug
DEBUG = os.environ.get("DEBUG", "True") == "True"

#  Dozwolone hosty (na Railway najlepiej *)
ALLOWED_HOSTS = ["braspol.pl", "www.braspol.pl", "0s2qosca.up.railway.app", 'brspweb-production.up.railway.app']


CSRF_TRUSTED_ORIGINS = [
    "https://www.braspol.pl",
    "https://braspol.pl",
    "https://brspweb-production.up.railway.app",  #dla testów
]

# settings.py
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


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
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS' : 'drf_spectacular.openapi.AutoSchema'
}

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

# Zdjecia
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

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

# weź URL z kilku możliwych nazw, bo na Railway bywa różnie
_DB_URL = (
    os.getenv("DATABASE_PUBLIC_URL")
    or os.getenv("RAILWAY_DATABASE_URL")
    or os.getenv("POSTGRES_URL")          # czasem plugin wystawia też taką zmienną
)

if not _DB_URL:
    # WOLNO użyć SQLite TYLKO lokalnie. Na produkcji to skasuj!
    _DB_URL = "sqlite:///db.sqlite3"



DATABASES = {
    "default": dj_database_url.config(
        default=f"postgresql://postgres:HLofOUuncDNWONKnPhOdJheaUPWcrfWO@turntable.proxy.rlwy.net:24544/railway"
    )
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
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

#  Pliki media (jeżeli używasz)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

#  Domyślne auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"