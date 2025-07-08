"""
Module: Unit tests for environment loading and cache settings.

Tests:
- .env file is loaded when not in testing mode.
- Correct cache backend is selected based on TESTING and REDIS_URL.
"""

import importlib
import sys
import os
from pathlib import Path

import pytest
import environ

import loan_app.settings as settings_module


@pytest.mark.usefixtures("monkeypatch")
def test_read_env_called_when_not_testing(monkeypatch) -> None:
    """
    Verify that environ.Env.read_env is invoked when TESTING=False.
    Simulate non-test run by removing 'pytest' from sys.argv.
    """
    # Flag to record read_env invocation
    called: dict[str, str] = {}

    def fake_read_env(self, env_file: str) -> None:
        # Record the path passed to read_env
        called["file"] = env_file

    # Monkeypatch read_env
    monkeypatch.setattr(environ.Env, "read_env", fake_read_env)
    # Simulate non-testing invocation
    monkeypatch.setattr(sys, "argv", ["manage.py", "runserver"])
    # Reload settings to trigger read_env
    importlib.reload(settings_module)
    # Expect .env in the BASE_DIR path
    env_path = Path(settings_module.BASE_DIR) / ".env"
    assert "file" in called, "read_env was not called"
    assert called["file"] == str(env_path)


@pytest.mark.parametrize(
    "argv,redis_url,expected_backend",
    [
        # Testing True => always locmem cache
        (["pytest"], "", "django.core.cache.backends.locmem.Lo"
                     "cMemCache"),
        # Testing False + REDIS_URL => RedisCache
        (["manage.py"], "redis://x", "django_redis.cache.RedisCa"
                                     "che"),
        # Testing False + no REDIS_URL => locmem fallback
        (["manage.py"], "", "django.core.cache.backends.locmem.Lo"
                           "cMemCache"),
    ],
)
@pytest.mark.usefixtures("monkeypatch")
def test_cache_backend_selection(
    monkeypatch, argv: list[str], redis_url: str, expected_backend: str
) -> None:
    """
    Ensure CACHES['default']['BACKEND'] matches expected based
    on TESTING and REDIS_URL.
    """
    # Monkeypatch sys.argv and environment
    monkeypatch.setenv("REDIS_URL", redis_url)
    monkeypatch.setattr(sys, "argv", argv)
    # Reload settings to apply new env
    importlib.reload(settings_module)
    # Extract backend setting
    backend = settings_module.CACHES["default"]["BACKEND"]
    assert backend == expected_backend
