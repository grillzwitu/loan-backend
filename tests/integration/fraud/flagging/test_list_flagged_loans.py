"""
Module: Integration test for listing flagged loans endpoint.
"""

from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from fraud.services import run_fraud_checks
from loan.models import LoanApplication


@pytest.mark.django_db
def test_flagged_loans_endpoint_admin(
    admin_client: APIClient,
    user: Any
) -> None:
    """Verify that an admin user can list loans flagged for fraud, including
    nested fraud flags."""
    loan = LoanApplication.objects.create(user=user, amount=6000000)
    reasons = run_fraud_checks(loan)
    assert reasons
    url = reverse("flagged-loans")
    response = admin_client.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "results" in response.data and "count" in response.data
    items = response.data["results"]
    flagged = next(item for item in items if item["id"] == loan.pk)
    assert flagged["status"] == "FLAGGED"
    assert "fraud_flags" in flagged
