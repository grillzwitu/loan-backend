import os
from pathlib import Path
import datetime
import environ

env = environ.Env(DEBUG=(bool, False))
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = env("SECRET_KEY", default="unsafe-default-key")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("CORS_ALLOWED_ORIGINS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "corsheaders", "rest_framework", "rest_framework_simplejwt", "drf_yasg",
    "users", "loan", "fraud",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware","django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware","django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware","django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware","django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "loan_app.urls"
TEMPLATES = [{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[],"APP_DIRS":True,"OPTIONS":{"context_processors":["django.template.context_processors.debug","django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"],},},]
WSGI_APPLICATION = "loan_app.wsgi.application"

if env.bool("USE_SQLITE", default=True):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME", default="loan_db"),
            "USER": env("DB_USER", default="loan_user"),
            "PASSWORD": env("DB_PASSWORD", default="loan_password"),
            "HOST": env("DB_HOST", default="db"),
            "PORT": env("DB_PORT", default="5432"),
        }
    }

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://redis:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

STATIC_URL = "/static/"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication"
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(seconds=env("JWT_EXPIRATION_DELTA_SECONDS", default=300)),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(seconds=env("JWT_REFRESH_EXPIRATION_DELTA_SECONDS", default=86400)),
    "SIGNING_KEY": env("JWT_SECRET_KEY", default=SECRET_KEY),
    "ALGORITHM": env("JWT_ALGORITHM", default="HS256"),
}

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

SWAGGER_SETTINGS = {"USE_SESSION_AUTH":False,"SECURITY_DEFINITIONS":{"Bearer":{"type":"apiKey","name":"Authorization","in":"header"}},}
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {name} {message}",
            "style": "{"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose"
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO"
    }
}