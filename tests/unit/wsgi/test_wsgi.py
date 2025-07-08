"""
Module: Unit tests for `loan_app/wsgi.py`.

Ensures WSGI setup loads correct settings module and
that the application object is callable.
"""

import importlib
import os
from typing import Any
import pytest


@pytest.mark.usefixtures("monkeypatch")
def test_default_settings_module(
    monkeypatch
) -> None:
    """
    Ensure DJANGO_SETTINGS_MODULE is set to
    'loan_app.settings' when wsgi is loaded.
    """
    # Remove existing env var to simulate fresh load
    monkeypatch.delenv(
        "DJANGO_SETTINGS_MODULE", raising=False
    )
    # Reload wsgi module to trigger os.environ.setdefault
    wsgi_module = importlib.reload(
        importlib.import_module("loan_app.wsgi")
    )
    # Verify environment var is set correctly
    assert os.environ["DJANGO_SETTINGS_MODULE"] == \
        "loan_app.settings"
    # application object should exist and be callable
    app_obj: Any = getattr(
        wsgi_module, "application", None
    )
    assert app_obj is not None
    assert callable(app_obj)


def test_wsgi_application_callable() -> None:
    """
    Verify that the WSGI application attribute is callable.
    """
    import loan_app.wsgi as wsgi_module

    app: Any = wsgi_module.application
    assert callable(app)
