"""
Module: Integration test for forbidden access to flagged loans endpoint.
"""

from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from fraud.services import run_fraud_checks
from loan.models import LoanApplication


@pytest.mark.django_db
def test_flagged_loans_endpoint_forbidden_regular_user(
    auth_client: APIClient, user: Any
) -> None:
    """Verify that a regular user is forbidden from listing flagged loans."""
    loan = LoanApplication.objects.create(user=user, amount=6000000)
    run_fraud_checks(loan)
    url = reverse("flagged-loans")
    response = auth_client.get(url, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN
