"""
Module: Integration test for historical flagged loans endpoint (admin).
"""

from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from fraud.services import run_fraud_checks
from loan.models import LoanApplication


@pytest.mark.django_db
def test_flagged_loans_history_endpoint_admin(
    admin_client: APIClient, user: Any
) -> None:
    """
    Verify that an admin user can list all loans ever flagged.
    """
    loan = LoanApplication.objects.create(user=user, amount=6000000)
    reasons = run_fraud_checks(loan)
    assert reasons
    loan.withdraw()
    url = reverse("flagged-loans-history")
    response = admin_client.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "results" in response.data
    assert any(item["id"] == loan.pk for item in response.data["results"])
