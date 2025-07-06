"""
Module: Strictly typed tests for admin REST API endpoints on LoanApplication.

These tests verify that admin users can approve, reject, and flag loan applications via API endpoints,
with detailed type hints and comprehensive docstrings following project standards.
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response
from typing import Any, Dict

from loan.models import LoanApplication
from fraud.models import FraudFlag

User = get_user_model()

@pytest.mark.django_db
def test_admin_approve_pending_loan(admin_client: APIClient, user: User) -> None:
    """
    Verify that an admin user can approve a pending loan application.

    Args:
        admin_client (APIClient): Client authenticated as superuser.
        user (User): Test user who created the loan.

    Returns:
        None
    """
    loan: LoanApplication = LoanApplication.objects.create(user=user, amount=1500)
    assert loan.status == "PENDING"
    url: str = reverse("loan-approve", args=[loan.id])
    response: Response = admin_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("status") == "APPROVED"

@pytest.mark.django_db
def test_admin_reject_pending_loan(admin_client: APIClient, user: User) -> None:
    """
    Verify that an admin user can reject a pending loan application.

    Args:
        admin_client (APIClient): Client authenticated as superuser.
        user (User): Test user who created the loan.

    Returns:
        None
    """
    loan: LoanApplication = LoanApplication.objects.create(user=user, amount=2000)
    assert loan.status == "PENDING"
    url: str = reverse("loan-reject", args=[loan.id])
    response: Response = admin_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("status") == "REJECTED"

@pytest.mark.django_db
def test_admin_flag_pending_loan(admin_client: APIClient, user: User) -> None:
    """
    Verify that an admin user can manually flag a pending loan application.

    Args:
        admin_client (APIClient): Client authenticated as superuser.
        user (User): Test user who created the loan.

    Returns:
        None
    """
    loan: LoanApplication = LoanApplication.objects.create(user=user, amount=2500)
    assert loan.status == "PENDING"
    url: str = reverse("loan-flag", args=[loan.id])
    data: Dict[str, Any] = {"reason": "suspected fraud"}
    response: Response = admin_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("status") == "FLAGGED"
    flags = FraudFlag.objects.filter(loan=loan)
    assert flags.count() == 1
    assert flags.first().reason == "suspected fraud"

@pytest.mark.django_db
def test_admin_cannot_approve_non_pending_or_flagged(admin_client: APIClient, user: User) -> None:
    """
    Verify that an admin cannot approve loans that are neither pending nor flagged.

    Args:
        admin_client (APIClient): Client authenticated as superuser.
        user (User): Test user who created the loan.

    Returns:
        None
    """
    loan: LoanApplication = LoanApplication.objects.create(user=user, amount=3000)
    loan.status = "REJECTED"
    loan.save(update_fields=["status"])
    url: str = reverse("loan-approve", args=[loan.id])
    response: Response = admin_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_admin_cannot_reject_non_pending_or_flagged(admin_client: APIClient, user: User) -> None:
    """
    Verify that an admin cannot reject loans that are neither pending nor flagged.

    Args:
        admin_client (APIClient): Client authenticated as superuser.
        user (User): Test user who created the loan.

    Returns:
        None
    """
    loan: LoanApplication = LoanApplication.objects.create(user=user, amount=3000)
    loan.status = "APPROVED"
    loan.save(update_fields=["status"])
    url: str = reverse("loan-reject", args=[loan.id])
    response: Response = admin_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_admin_cannot_flag_non_pending(admin_client: APIClient, user: User) -> None:
    """
    Verify that an admin cannot flag loans that are not pending.

    Args:
        admin_client (APIClient): Client authenticated as superuser.
        user (User): Test user who created the loan.

    Returns:
        None
    """
    loan: LoanApplication = LoanApplication.objects.create(user=user, amount=4000)
    loan.status = "APPROVED"
    loan.save(update_fields=["status"])
    url: str = reverse("loan-flag", args=[loan.id])
    response: Response = admin_client.post(url, {"reason": "spam"}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST