"""
Module: Strictly typed tests for permissions on loan endpoints for regular and admin users.

These tests ensure that regular users can only view their own loans and cannot perform admin actions,
and that admin users have appropriate access to all loan API endpoints.
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response
from typing import Any, List

from loan.models import LoanApplication

User = get_user_model()

@pytest.mark.django_db
def test_regular_user_list_loans(auth_client: APIClient, user: User) -> None:
    """
    Verify that a regular user can only list their own loan applications.

    Args:
        auth_client (APIClient): Authenticated client for regular user.
        user (User): Test user whose loans should be listed.

    Returns:
        None
    """
    other_user: User = User.objects.create_user(
        username="other", email="other@example.com", password="password"
    )
    loan1: LoanApplication = LoanApplication.objects.create(user=user, amount=100)
    loan2: LoanApplication = LoanApplication.objects.create(user=other_user, amount=200)
    url: str = reverse("loan-list-create")
    response: Response = auth_client.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK
    ids: List[int] = [item["id"] for item in response.data]
    assert loan1.id in ids
    assert loan2.id not in ids

@pytest.mark.django_db
def test_regular_user_cannot_retrieve_other_loan(auth_client: APIClient, user: User) -> None:
    """
    Verify that a regular user cannot retrieve another user's loan.

    Args:
        auth_client (APIClient): Authenticated client for regular user.
        user (User): Test user different from the loan owner.

    Returns:
        None
    """
    other_user: User = User.objects.create_user(
        username="other", email="other@example.com", password="password"
    )
    loan: LoanApplication = LoanApplication.objects.create(user=other_user, amount=300)
    url: str = reverse("loan-detail", args=[loan.id])
    response: Response = auth_client.get(url, format="json")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_admin_user_list_all_loans(admin_client: APIClient, user: User) -> None:
    """
    Verify that an admin user can list all loans regardless of owner.

    Args:
        admin_client (APIClient): Authenticated superuser client.
        user (User): Regular user for loan creation.

    Returns:
        None
    """
    other_user: User = User.objects.create_user(
        username="other2", email="other2@example.com", password="password"
    )
    loan1: LoanApplication = LoanApplication.objects.create(user=user, amount=150)
    loan2: LoanApplication = LoanApplication.objects.create(user=other_user, amount=250)
    url: str = reverse("loan-list-create")
    response: Response = admin_client.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK
    ids: List[int] = [item["id"] for item in response.data]
    assert loan1.id in ids
    assert loan2.id in ids

@pytest.mark.django_db
def test_admin_user_retrieve_any_loan(admin_client: APIClient, user: User) -> None:
    """
    Verify that an admin user can retrieve any loan by ID.

    Args:
        admin_client (APIClient): Authenticated superuser client.
        user (User): Regular user for loan creation.

    Returns:
        None
    """
    loan: LoanApplication = LoanApplication.objects.create(user=user, amount=300)
    url: str = reverse("loan-detail", args=[loan.id])
    response: Response = admin_client.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == loan.id

@pytest.mark.django_db
def test_regular_user_cannot_access_admin_endpoints(auth_client: APIClient, user: User) -> None:
    """
    Verify that regular users cannot access admin-only endpoints for approve, reject, and flag.

    Args:
        auth_client (APIClient): Authenticated client for regular user.
        user (User): Regular user for loan creation.

    Returns:
        None
    """
    loan: LoanApplication = LoanApplication.objects.create(user=user, amount=400)
    for action in ("approve", "reject", "flag"):
        url: str = reverse(f"loan-{action}", args=[loan.id])
        response: Response = auth_client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_admin_user_can_approve_flagged_loan(admin_client: APIClient, user: User) -> None:
    """
    Verify that an admin can approve loans that have been flagged.

    Args:
        admin_client (APIClient): Authenticated superuser client.
        user (User): Regular user who created the loan.

    Returns:
        None
    """
    loan: LoanApplication = LoanApplication.objects.create(user=user, amount=500)
    loan.status = "FLAGGED"
    loan.save(update_fields=["status"])
    url: str = reverse("loan-approve", args=[loan.id])
    response: Response = admin_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("status") == "APPROVED"

@pytest.mark.django_db
def test_admin_user_can_reject_flagged_loan(admin_client: APIClient, user: User) -> None:
    """
    Verify that an admin can reject loans that have been flagged.

    Args:
        admin_client (APIClient): Authenticated superuser client.
        user (User): Regular user who created the loan.

    Returns:
        None
    """
    loan: LoanApplication = LoanApplication.objects.create(user=user, amount=600)
    loan.status = "FLAGGED"
    loan.save(update_fields=["status"])
    url: str = reverse("loan-reject", args=[loan.id])
    response: Response = admin_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("status") == "REJECTED"