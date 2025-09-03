from .base import *

import os
import dj_database_url

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]



# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv("DATABASE_URL", "sqlite:///db.sqlite3"),
        conn_max_age=600,
        ssl_require=False
    )
}

SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = "None"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
CORS_ALLOW_CREDENTIALS = True
