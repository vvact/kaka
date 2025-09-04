from .base import *
import os
from decouple import config

# ----------------------------
# Debug & Allowed Hosts
# ----------------------------
DEBUG = False

ALLOWED_HOSTS = [
    "gentlemanwell.shop",
    "www.gentlemanwell.shop",
    "api.gentlemanwell.shop",
    "localhost", 
    "127.0.0.1",        
]

# ----------------------------
# Security cookies
# ----------------------------
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"

# ----------------------------
# CORS & CSRF
# ----------------------------
CORS_ALLOWED_ORIGINS = [
    "https://www.gentlemanwell.shop",
    "https://api.gentlemanwell.shop",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://emoney-ashy.vercel.app",
]
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "https://gentlemanwell.shop",
    "https://www.gentlemanwell.shop",
    "https://api.gentlemanwell.shop",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://emoney-ashy.vercel.app",
]

# ----------------------------
# PostgreSQL for production database
# ----------------------------
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

# ----------------------------
# Optional: Production-only security headers
# ----------------------------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# ----------------------------
# Optional: Logging
# ----------------------------
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'root': {
#         'handlers': ['console'],
#         'level': 'INFO',
#     },
# }
