"""
Module: Integration test for admin flag endpoint.
"""

from typing import Any, Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from fraud.models import FraudFlag
from loan.models import LoanApplication


@pytest.mark.django_db
def test_admin_flag_pending_loan(admin_client: APIClient, user: Any) -> None:
    """Verify that an admin user can flag a pending loan application."""
    loan = LoanApplication.objects.create(user=user, amount=2500)
    assert loan.status == "PENDING"
    url = reverse("loan-flag", args=[loan.pk])
    data: Dict[str, Any] = {"reason": "suspected fraud"}
    response = admin_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("status") == "FLAGGED"
    flags = FraudFlag.objects.filter(loan=loan)
    assert flags.count() == 1
    assert flags.first().reason == "suspected fraud"
