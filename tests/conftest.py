"""
conftest.py: Global pytest configuration and fixtures.

This module defines fixtures applied to all tests under the
`tests/` directory. It must reside in that directory so pytest can
auto-discover fixtures (cache clearing, APIClient instances, user
and admin setup) across the suite without explicit imports.

Available fixtures:
- clear_cache (autouse): Clears Django cache before each test,
  isolating caching behavior.
- api_client: Provides DRF APIClient for HTTP requests in unit and
  integration tests.
- auth_client: Provides an authenticated APIClient with a JWT token
  for the default user fixture.
- user: Creates a default test user for authentication-related tests.
- admin_user: Creates a superuser for admin-level tests.
- admin_client: Provides an authenticated APIClient for a superuser to
  test privileged endpoints.

Keeping configuration here promotes reuse, reduces duplication, and
ensures consistent test setup without manual imports.
"""

from typing import Any

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear Django cache before each test to isolate caching behavior."""
    cache.clear()


@pytest.fixture
def api_client() -> APIClient:
    """Returns an instance of the DRF APIClient for making HTTP requests."""
    return APIClient()


@pytest.fixture
def user(db) -> Any:
    """Create and return a default test user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password",
    )


@pytest.fixture
def auth_client(api_client: APIClient, user: Any) -> APIClient:
    """
    Returns an APIClient,
    authenticated with a JWT access token for the test user.
    """
    login_data = {"username": user.username, "password": "password"}
    response = api_client.post(
        "/api/users/login/",
        login_data,
        format="json",
    )
    access_token = response.data.get("access")
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return api_client


@pytest.fixture
def admin_user(db) -> Any:
    """Create and return a superuser for admin tests."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="password",
    )


@pytest.fixture
def admin_client(api_client: APIClient, admin_user: Any) -> APIClient:
    """Returns an APIClient authenticated as a superuser."""
    login_data = {"username": admin_user.username, "password": "password"}
    response = api_client.post(
        "/api/users/login/",
        login_data,
        format="json",
    )
    access_token = response.data.get("access")
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return api_client
