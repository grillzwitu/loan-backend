"""
Module: Integration test for loan withdraw endpoint.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_withdraw_loan_endpoint(auth_client: APIClient) -> None:
    """
    Test withdrawing a pending or non-pending loan via API and status updates.
    """
    list_url = reverse("loan-list-create")
    create_resp = auth_client.post(list_url, {"amount": "1000.00"}, format="json")
    assert create_resp.status_code == status.HTTP_201_CREATED
    loan_id = create_resp.data["id"]

    withdraw_url = reverse("loan-withdraw", args=[loan_id])
    withdraw_resp = auth_client.post(withdraw_url, {}, format="json")
    assert withdraw_resp.status_code == status.HTTP_400_BAD_REQUEST

    detail_url = reverse("loan-detail", args=[loan_id])
    detail_resp = auth_client.get(detail_url, format="json")
    assert detail_resp.data["status"] == "APPROVED"

    withdraw_again_resp = auth_client.post(withdraw_url, {}, format="json")
    assert withdraw_again_resp.status_code == status.HTTP_400_BAD_REQUEST
