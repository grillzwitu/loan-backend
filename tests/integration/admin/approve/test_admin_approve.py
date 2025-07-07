"""
Module: Integration test for admin approval endpoint.
"""

from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from loan.models import LoanApplication


@pytest.mark.django_db
def test_admin_approve_pending_loan(admin_client: APIClient, user: Any) -> None:
    """
    Verify that an admin user can approve a pending loan application.
    """
    loan = LoanApplication.objects.create(user=user, amount=1500)
    assert loan.status == "PENDING"
    url = reverse("loan-approve", args=[loan.pk])
    response = admin_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("status") == "APPROVED"
