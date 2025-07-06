import pytest
from typing import Any

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """
    Returns an instance of the DRF APIClient for making HTTP
    requests in tests.
    """
    return APIClient()


@pytest.fixture
def user(db) -> Any:
    """
    Create and return a default test user.
    """
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password",
    )


@pytest.fixture
def auth_client(api_client: APIClient, user: Any) -> APIClient:
    """
    Returns an APIClient authenticated with a JWT access token
    for the test user.
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
    """
    Create and return a superuser for admin tests.
    """
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="password",
    )


@pytest.fixture
def admin_client(api_client: APIClient, admin_user: Any) -> APIClient:
    """
    Returns an APIClient authenticated as a superuser.
    """
    login_data = {"username": admin_user.username, "password": "password"}
    response = api_client.post(
        "/api/users/login/",
        login_data,
        format="json",
    )
    access_token = response.data.get("access")
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return api_client
