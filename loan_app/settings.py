"""
Module: Django settings for loan_backend project.

Configures environment loading, installed apps, middleware, databases, caching,
authentication, Swagger, CORS, and logging for the Loan Backend service.
"""
import logging
import os
from pathlib import Path
import datetime
import environ
from typing import Any, Dict

env: environ.Env = environ.Env(DEBUG=(bool, False))
env.read_env()

BASE_DIR: Path = Path(__file__).resolve().parent.parent
SECRET_KEY: str = env("SECRET_KEY", default="unsafe-default-key")
DEBUG: bool = env("DEBUG")
ALLOWED_HOSTS: list[str] = env.list("CORS_ALLOWED_ORIGINS", default=[])

# List of Django core, third-party, and local apps registered with this project
INSTALLED_APPS: list[str] = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "corsheaders", "rest_framework", "rest_framework_simplejwt", "drf_yasg",
    "users", "loan", "fraud",
]

# Ordered list of middleware for request/response processing (security, sessions, CORS, etc.)
MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware","django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware","django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware","django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware","django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF: str = "loan_app.urls"

"""Templates configuration: DjangoTemplates engine and context processors."""
TEMPLATES: list[dict[str, Any]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    },
]

"""WSGI application entry point for WSGI servers."""
WSGI_APPLICATION: str = "loan_app.wsgi.application"

# Database configuration: use SQLite for local dev or PostgreSQL per environment variables
DATABASES: Dict[str, Any]
# Database configuration: SQLite for local development or PostgreSQL via environment
DATABASES: dict[str, Any]
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

# Cache configuration: Redis-backed cache via django-redis
CACHES: Dict[str, Any] = {
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
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(seconds=env("JWT_EXPIRATION_DELTA_SECONDS", default=300)),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(seconds=env("JWT_REFRESH_EXPIRATION_DELTA_SECONDS", default=86400)),
    "SIGNING_KEY": env("JWT_SECRET_KEY", default=SECRET_KEY),
    "ALGORITHM": env("JWT_ALGORITHM", default="HS256"),
}

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

# Swagger / OpenAPI settings for documentation UI (Swagger & Redoc)
SWAGGER_SETTINGS: Dict[str, Any] = {
    "USE_SESSION_AUTH": False,
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header"
        }
    }
    
}

# Silence drf_yasg deprecation warning for changed renderer formats
SWAGGER_USE_COMPAT_RENDERERS: bool = False

# Logging configuration: formatters, handlers, and root logger settings
LOGGING: Dict[str, Any] = {
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
