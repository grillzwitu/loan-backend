"""
Module: Integration test for invalid admin actions on loan endpoints.
"""

from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from loan.models import LoanApplication


@pytest.mark.django_db
def test_admin_cannot_approve_non_pending_or_flagged(
    admin_client: APIClient, user: Any
) -> None:
    """
    Verify that an admin cannot approve loans that are neither pending nor flagged.
    """
    loan = LoanApplication.objects.create(user=user, amount=3000)
    loan.status = "REJECTED"
    loan.save(update_fields=["status"])
    url = reverse("loan-approve", args=[loan.pk])
    response = admin_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_cannot_reject_non_pending_or_flagged(
    admin_client: APIClient, user: Any
) -> None:
    """
    Verify that an admin cannot reject loans that are neither pending nor flagged.
    """
    loan = LoanApplication.objects.create(user=user, amount=3000)
    loan.status = "APPROVED"
    loan.save(update_fields=["status"])
    url = reverse("loan-reject", args=[loan.pk])
    response = admin_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_cannot_flag_non_pending(admin_client: APIClient, user: Any) -> None:
    """
    Verify that an admin cannot flag loans that are not pending.
    """
    loan = LoanApplication.objects.create(user=user, amount=4000)
    loan.status = "APPROVED"
    loan.save(update_fields=["status"])
    url = reverse("loan-flag", args=[loan.pk])
    response = admin_client.post(url, {"reason": "spam"}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN
