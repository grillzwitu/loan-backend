"""
Module: Integration test for admin rejection endpoint.
"""

from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from loan.models import LoanApplication


@pytest.mark.django_db
def test_admin_reject_pending_loan(admin_client: APIClient, user: Any) -> None:
    """Verify that an admin user can reject a pending loan application."""
    loan = LoanApplication.objects.create(user=user, amount=2000)
    assert loan.status == "PENDING"
    url = reverse("loan-reject", args=[loan.pk])
    response = admin_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("status") == "REJECTED"
