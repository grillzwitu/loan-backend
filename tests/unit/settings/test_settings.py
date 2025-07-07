"""
Module: Unit tests for the Loan Backend settings fallback logic.
Verifies DATABASES configuration for SQLite and PostgreSQL based on
the USE_SQLITE flag.
"""

import importlib

import pytest
from pytest import MonkeyPatch

# from pathlib import Path (unused)



@pytest.mark.parametrize(
    "use_sqlite, expected_engine",
    [
        (True, "django.db.backends.sqlite3"),
        (False, "django.db.backends.postgresql"),
    ],
)
def test_database_engine_fallback(
    monkeypatch: MonkeyPatch, use_sqlite: bool, expected_engine: str
) -> None:
    """
    Verify DATABASES setting falls back to SQLite or PostgreSQL based
    on USE_SQLITE env var.
    """
    # Arrange environment variables for test
    monkeypatch.setenv("USE_SQLITE", str(use_sqlite))
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "password")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")

    # Reload settings module to apply new environment
    import loan_app.settings as settings_module

    importlib.reload(settings_module)

    # Act: inspect the DATABASES config
    engine = settings_module.DATABASES["default"]["ENGINE"]

    # Assert correct engine based on USE_SQLITE
    assert engine == expected_engine
    if use_sqlite:
        expected_name = settings_module.BASE_DIR / "db.sqlite3"
        assert settings_module.DATABASES["default"]["NAME"] == expected_name
    else:
        assert settings_module.DATABASES["default"]["NAME"] == "test_db"
