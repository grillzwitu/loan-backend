"""
Module: Strictly typed tests for the flagged loans listing endpoint.

These tests ensure that flagged loans are recorded via the FraudFlag
model, that admin users can list flagged loans with nested fraud
reasons, and that regular users are forbidden from accessing this
endpoint.
"""

from typing import Any, Dict, List

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from fraud.services import run_fraud_checks
from loan.models import LoanApplication


@pytest.mark.django_db
def test_flagged_loans_endpoint_admin(
    admin_client: APIClient,
    user: Any,
) -> None:
    """
    Verify that an admin user can list loans flagged for fraud,
    and that each returned loan includes its nested fraud flags.

    Args:
        admin_client (APIClient): Authenticated superuser client.
        user (User): Regular user who applies for loans.

    Returns:
        None
    """
    # Create and flag a loan via fraud service
    loan: LoanApplication = LoanApplication.objects.create(
        user=user,
        amount=6000000,
    )
    reasons: List[str] = run_fraud_checks(loan)
    assert reasons  # Ensure at least one reason was flagged
    url: str = reverse("flagged-loans")
    response: Response = admin_client.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK
    # Pagination structure
    assert "results" in response.data and "count" in response.data
    assert response.data["count"] >= 1
    result_items: List[Any] = response.data["results"]
    # Verify first result matches our flagged loan
    flagged_data: Any = next(
        item
        for item in result_items
        if item["id"] == loan.pk
    )
    assert flagged_data["id"] == loan.pk
    assert flagged_data["status"] == "FLAGGED"
    # Nested fraud flags included
    assert "fraud_flags" in flagged_data
    nested_reasons: List[Dict[str, Any]] = flagged_data["fraud_flags"]
    assert nested_reasons
    # Check that reasons match
    recorded_reasons: List[str] = [flag["reason"] for flag in nested_reasons]
    for reason in reasons:
        assert reason in recorded_reasons


@pytest.mark.django_db
def test_flagged_loans_endpoint_forbidden_regular_user(
    auth_client: APIClient,
    user: Any,
) -> None:
    """
    Verify that a regular user is forbidden from listing flagged loans.

    Args:
        auth_client (APIClient): Authenticated client for regular user.
        user (User): Regular user test fixture.

    Returns:
        None
    """
    loan: LoanApplication = LoanApplication.objects.create(
        user=user,
        amount=6000000,
    )
    run_fraud_checks(loan)
    url: str = reverse("flagged-loans")
    response: Response = auth_client.get(url, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN
