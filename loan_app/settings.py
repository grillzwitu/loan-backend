"""
Module: Django settings for loan_backend project.

Configures environment loading, installed apps, middleware, databases, caching,
authentication, Swagger, CORS, and logging for the Loan Backend service.
"""

import datetime
import os
import sys
from pathlib import Path
from typing import Any, Dict

import environ  # type: ignore[import-untyped]

# ------------------------------------------------------------------------------
# Environment variables
# ------------------------------------------------------------------------------
env: environ.Env = environ.Env(DEBUG=(bool, False))
BASE_DIR: Path = Path(__file__).resolve().parent.parent
# Detect test environment via pytest invocation
TESTING: bool = any("pytest" in arg for arg in sys.argv)
# Load .env file only when not testing
if not TESTING:
    env.read_env(env_file=str(BASE_DIR / ".env"))

# ------------------------------------------------------------------------------
# Security settings
# ------------------------------------------------------------------------------
# SECRET_KEY: Django security key (keep this secret in production)
SECRET_KEY: str = env("SECRET_KEY", default="unsafe-default-key")
# DEBUG: Toggle debug mode (use False in production)
DEBUG: bool = env("DEBUG")
# ALLOWED_HOSTS: Hosts allowed to serve this application when DEBUG=False
ALLOWED_HOSTS: list[str] = env.list(
    "ALLOWED_HOSTS", default=[]
) + [  # from .env or environment variables
    "127.0.0.1",
    "localhost",
]

# ------------------------------------------------------------------------------
# Application definition
# ------------------------------------------------------------------------------
INSTALLED_APPS: list[str] = [
    # Django core apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "corsheaders",  # Handle Cross-Origin Resource Sharing
    "rest_framework",  # Django REST Framework for APIs
    "rest_framework_simplejwt",  # JWT authentication support
    "drf_yasg",  # Swagger/OpenAPI documentation
    # Local apps
    "users",
    "loan",
    "fraud",
]

# ------------------------------------------------------------------------------
# Middleware configuration
# ------------------------------------------------------------------------------
MIDDLEWARE: list[str] = [
    # Security and session management
    "django.middleware.security.SecurityMiddleware",
    *([] if TESTING else ["whitenoise.middleware.WhiteNoiseMiddleware"]),
    "django.contrib.sessions.middleware.SessionMiddleware",
    # CORS handling
    "corsheaders.middleware.CorsMiddleware",
    # Common HTTP middleware
    "django.middleware.common.CommonMiddleware",
    # CSRF protection
    "django.middleware.csrf.CsrfViewMiddleware",
    # Authentication and messaging
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # Clickjacking protection
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ------------------------------------------------------------------------------
# URL configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF: str = "loan_app.urls"

# ------------------------------------------------------------------------------
# Templates configuration
# ------------------------------------------------------------------------------
TEMPLATES: list[Dict[str, Any]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # Add custom template directories here
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Default template context processors
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ------------------------------------------------------------------------------
# WSGI application
# ------------------------------------------------------------------------------
WSGI_APPLICATION: str = "loan_app.wsgi.application"

# ------------------------------------------------------------------------------
# Database configuration
# ------------------------------------------------------------------------------
# Default: SQLite for local development; set USE_SQLITE=False for PostgreSQL
# Database configuration
DATABASES: Dict[str, Any]
if os.getenv("USE_SQLITE", "True").lower() in ("true", "1", "yes"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # PostgreSQL configuration
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

# ------------------------------------------------------------------------------
# Cache configuration
# ------------------------------------------------------------------------------
# REDIS_URL: URL for Redis cache (e.g. redis://localhost:6379/0)
REDIS_URL: str | None = env("REDIS_URL", default=None)

CACHES: Dict[str, Any]
if TESTING:
    # In-memory cache during tests for isolation and speed
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-locmem",
        }
    }
elif REDIS_URL:
    # Redis cache in production/staging
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                # Prevent Redis errors from crashing app
                "CLIENT_CLASS": ("django_redis.client.DefaultClient"),
                "IGNORE_EXCEPTIONS": True,
            },
        }
    }
else:
    # Fallback to thread-safe in-memory cache
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "locmem-default",
        }
    }

# ------------------------------------------------------------------------------
# Email backend
# ------------------------------------------------------------------------------
if TESTING:
    # Store emails in memory during tests instead of sending
    EMAIL_BACKEND: str = "django.core.mail.backends.locmem.EmailBackend"

# ------------------------------------------------------------------------------
# Static files (CSS, JavaScript, Images)
# ------------------------------------------------------------------------------
STATIC_URL: str = "/static/"
STATIC_ROOT: Path = BASE_DIR / "staticfiles"
STATICFILES_STORAGE: str = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ------------------------------------------------------------------------------
# Django REST Framework configuration
# ------------------------------------------------------------------------------
REST_FRAMEWORK: Dict[str, Any] = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": ("rest_framework.pagination.PageNumberPagination"),
    "PAGE_SIZE": 10,
}

# ------------------------------------------------------------------------------
# Simple JWT (JSON Web Token) configuration
# ------------------------------------------------------------------------------
SIMPLE_JWT: Dict[str, Any] = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(
        seconds=env("JWT_EXPIRATION_DELTA_SECONDS", default=300)
    ),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(
        seconds=env("JWT_REFRESH_EXPIRATION_DELTA_SECONDS", default=86400)
    ),
    "SIGNING_KEY": env("JWT_SECRET_KEY", default=SECRET_KEY),
    "ALGORITHM": env("JWT_ALGORITHM", default="HS256"),
}

# ------------------------------------------------------------------------------
# Cross-Origin Resource Sharing (CORS)
# ------------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS: list[str] = env.list("CORS_ALLOWED_ORIGINS", default=[])

# ------------------------------------------------------------------------------
# Swagger / OpenAPI documentation settings
# ------------------------------------------------------------------------------
SWAGGER_SETTINGS: Dict[str, Any] = {
    "USE_SESSION_AUTH": False,
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        },
    },
}
SWAGGER_USE_COMPAT_RENDERERS: bool = False

# ------------------------------------------------------------------------------
# Logging configuration
# ------------------------------------------------------------------------------
LOGGING: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
