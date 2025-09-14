from datetime import timedelta
import os
from pathlib import Path
from decouple import config
import cloudinary



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Cloudinary Configuration
cloudinary.config(
    cloud_name=config('CLOUDINARY_CLOUD_NAME'),
    api_key=config('CLOUDINARY_API_KEY'),
    api_secret=config('CLOUDINARY_API_SECRET'),
)

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
}
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

# ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "185.122.164.139",
    "www.gentlemanwell.shop",
    "gentlemanwell.shop",
    "api.gentlemanwell.shop",
]


# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

]
LOGIN_REDIRECT_URL = '/admin/' 
THIRD_PARTY_APPS = [
    'whitenoise.runserver_nostatic',
    'cloudinary',
    'cloudinary_storage',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'widget_tweaks',

]

LOCAL_APPS = [
    'accounts',
    'products',
    'cart',
    'moments',
    'orders',
    'dashboard',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

SITE_ID = 1

# Allauth configuration
SOCIALACCOUNT_AUTO_SIGNUP = True

# Email-only authentication (modern allauth)
ACCOUNT_USER_MODEL_USERNAME_FIELD = None 
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']  
ACCOUNT_LOGIN_METHODS = {'email'}

# Google OAuth Configuration
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
            'prompt': 'select_account',
        },
        'METHOD': 'oauth2',
        'OAUTH_PKCE_ENABLED': True,
        'APP': {
            'client_id': config('GOOGLE_OAUTH_CLIENT_ID'),
            'secret': config('GOOGLE_OAUTH_CLIENT_SECRET'),
            'key': ''
        }
    }
}

# Default file storage for media
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'allauth.account.middleware.AccountMiddleware',

]

ROOT_URLCONF = "kaka.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "kaka.wsgi.application"




# customU User
AUTH_USER_MODEL = "accounts.User"

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-ke"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# =============================
# STATIC FILES
# =============================
STATIC_URL = '/static/'  # leading slash is required
STATICFILES_DIRS = [BASE_DIR / 'static']  # for development
STATIC_ROOT = BASE_DIR / 'staticfiles'   # where collectstatic will copy files

# Whitenoise (optional fallback if Nginx misses something)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =============================
# MEDIA FILES
# =============================
MEDIA_URL = '/media/'   # leading slash is required
MEDIA_ROOT = BASE_DIR / 'media'  # where uploaded media files will be stored


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny", 
    ),
}



SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=240),  # 4 hours
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "UPDATE_LAST_LOGIN": True,
}



# ------------------ SESSION ------------------
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_COOKIE_NAME = "ecomerec_session"
SESSION_COOKIE_AGE = 7 * 24 * 60 * 60
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = False


# Trusted origins for CSRF POST requests
CSRF_TRUSTED_ORIGINS = [
    "https://gentlemanwell.shop",
    "https://www.gentlemanwell.shop",
    "https://api.gentlemanwell.shop",
    "https://gentlemanwell.shop",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]


CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://gentlemanwell.shop",
    "https://www.gentlemanwell.shop",
    "https://api.gentlemanwell.shop",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True

DATA_UPLOAD_MAX_MEMORY_SIZE = 209715200 
FILE_UPLOAD_MAX_MEMORY_SIZE = 209715200 






