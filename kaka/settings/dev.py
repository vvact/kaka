from .base import *

import os
import dj_database_url

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Database
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL", "sqlite:///db.sqlite3"),
        conn_max_age=600,
        ssl_require=False,
    )
}

# ✅ Cookies (safe for local dev, works with Django admin & CSRF)
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = "Lax"   # "Lax" works locally, allows cookies
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = "Lax"

# ✅ CSRF Trusted Origins (required in Django 4+)
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# ✅ CORS (for your React frontend on Vite at port 5173)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
CORS_ALLOW_CREDENTIALS = True
