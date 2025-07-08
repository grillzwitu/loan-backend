"""
Module: Integration tests for authentication and token flow using Simple JWT.
"""

from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_user_registration_and_token_flow(api_client: APIClient) -> None:
    """Test registration endpoint and Simple JWT token issuance."""
    register_url = reverse("register")
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "pass1234",
    }
    response = api_client.post(
        register_url,
        data,
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert "user" in response.data
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_token_obtain_and_refresh(api_client: APIClient, user: Any) -> None:
    """Test login and token refresh endpoints using Simple JWT."""
    login_url = reverse("token_obtain_pair")
    refresh_url = reverse("token_refresh")
    credentials = {"username": user.username, "password": "password"}
    login_resp = api_client.post(
        login_url,
        credentials,
        format="json",
    )
    assert login_resp.status_code == status.HTTP_200_OK
    refresh_token = login_resp.data.get("refresh")
    assert refresh_token is not None

    refresh_resp = api_client.post(
        refresh_url,
        {"refresh": refresh_token},
        format="json",
    )
    assert refresh_resp.status_code == status.HTTP_200_OK
    assert "access" in refresh_resp.data


@pytest.mark.django_db
def test_logout_endpoint(auth_client: APIClient) -> None:
    """Test logout endpoint responds with HTTP 204 No Content."""
    logout_url = reverse("logout")
    resp = auth_client.post(
        logout_url,
        {},
        format="json",
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT
