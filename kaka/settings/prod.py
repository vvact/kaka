from .base import *
import os
from decouple import config

DEBUG = False
ALLOWED_HOSTS = [
    "gentlemanwell.shop",
    "www.gentlemanwell.shop",
    "api.gentlemanwell.shop",
]

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"

CORS_ALLOWED_ORIGINS = [
    "https://www.gentlemanwell.shop",
    "https://api.gentlemanwell.shop",
]
CORS_ALLOW_CREDENTIALS = True


# PostgreSQL for local products database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get("POSTGRES_DB", "manwell"),
        'USER': os.environ.get("POSTGRES_USER", "manwell"),
        'PASSWORD': os.environ.get("POSTGRES_PASSWORD", "buda123$"),
        'HOST': os.environ.get("POSTGRES_HOST", "localhost"),
        'PORT': os.environ.get("POSTGRES_PORT", "5432"),
    }
}
