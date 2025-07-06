"""
Module: Integration tests for loan backend API
endpoints with Simple JWT authentication.
"""

import pytest
from typing import Any
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_user_registration_and_token_flow(
    api_client: APIClient,
) -> None:
    """
    Test registration endpoint and Simple JWT token issuance.
    """
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
def test_token_obtain_and_refresh(
    api_client: APIClient,
    user: Any,
) -> None:
    """
    Test login and token refresh endpoints using Simple JWT.
    """
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
def test_logout_endpoint(
    auth_client: APIClient,
) -> None:
    """
    Test logout endpoint responds with HTTP 204 No Content.
    """
    logout_url = reverse("logout")
    resp = auth_client.post(
        logout_url,
        {},
        format="json",
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_loan_endpoints(
    auth_client: APIClient,
) -> None:
    """
    Test creating, listing, and retrieving LoanApplication via API endpoints.
    """
    # List initially empty
    list_url = reverse("loan-list-create")
    resp_list = auth_client.get(
        list_url,
        format="json",
    )
    assert resp_list.status_code == status.HTTP_200_OK
    assert resp_list.data["results"] == []
    assert resp_list.data["count"] == 0

    # Create and submit a loan
    create_data = {"amount": "500.00"}
    resp_create = auth_client.post(
        list_url,
        create_data,
        format="json",
    )
    assert resp_create.status_code == status.HTTP_201_CREATED
    loan_id = resp_create.data.get("id")
    assert resp_create.data.get("amount") == "500.00"
    # Loans passing fraud checks should be auto-approved
    assert resp_create.data.get("status") == "APPROVED"

    # Retrieve the created loan
    detail_url = reverse("loan-detail", args=[loan_id])
    resp_detail = auth_client.get(
        detail_url,
        format="json",
    )
    assert resp_detail.status_code == status.HTTP_200_OK
    assert resp_detail.data.get("id") == loan_id
    assert resp_detail.data.get("amount") == "500.00"


@pytest.mark.django_db
def test_withdraw_loan_endpoint(
    auth_client: APIClient,
) -> None:
    """
    Test withdrawing a pending loan via API endpoint and updating status.
    """
    # Create a new loan
    list_url = reverse("loan-list-create")
    create_resp = auth_client.post(
        list_url,
        {"amount": "1000.00"},
        format="json",
    )
    assert create_resp.status_code == status.HTTP_201_CREATED
    loan_id = create_resp.data["id"]

    # Attempt to withdraw a non-pending loan (auto-approved) should return 400
    withdraw_url = reverse("loan-withdraw", args=[loan_id])
    withdraw_resp = auth_client.post(
        withdraw_url,
        {},
        format="json",
    )
    assert withdraw_resp.status_code == status.HTTP_400_BAD_REQUEST

    # Verify status remains APPROVED
    detail_url = reverse("loan-detail", args=[loan_id])
    detail_resp = auth_client.get(detail_url, format="json")
    assert detail_resp.data["status"] == "APPROVED"

    # Attempt to withdraw again should return 400
    withdraw_again_resp = auth_client.post(
        withdraw_url,
        {},
        format="json",
    )
    assert withdraw_again_resp.status_code == status.HTTP_400_BAD_REQUEST
