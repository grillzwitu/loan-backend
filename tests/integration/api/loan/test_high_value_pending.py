"""
Module: Integration tests for high-value loan pending review endpoint.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_high_value_loan_pending_for_admin_review(
    auth_client: APIClient
) -> None:
    """Test that loans >1_000_000 remain pending."""
    list_url = reverse("loan-list-create")
    resp_create = auth_client.post(
        list_url,
        {"amount": "2000000.00"},
        format="json"
    )
    assert resp_create.status_code == status.HTTP_201_CREATED
    assert resp_create.data["status"] == "PENDING"
    loan_id = resp_create.data["id"]
    detail_url = reverse("loan-detail", args=[loan_id])
    detail_resp = auth_client.get(detail_url, format="json")
    assert detail_resp.status_code == status.HTTP_200_OK
    assert detail_resp.data["status"] == "PENDING"
    withdraw_url = reverse("loan-withdraw", args=[loan_id])
    withdraw_resp = auth_client.post(withdraw_url, {}, format="json")
    assert withdraw_resp.status_code == status.HTTP_204_NO_CONTENT
