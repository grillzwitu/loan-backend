"""
Module: Integration tests for LoanApplication list, create, and retrieve endpoints.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_list_create_and_retrieve_loan(auth_client: APIClient) -> None:
    """
    Test listing empty list, creating a loan, and retrieving it.
    """
    list_url = reverse("loan-list-create")
    resp_list = auth_client.get(list_url, format="json")
    assert resp_list.status_code == status.HTTP_200_OK
    assert resp_list.data["results"] == []
    assert resp_list.data["count"] == 0

    create_data = {"amount": "500.00"}
    resp_create = auth_client.post(list_url, create_data, format="json")
    assert resp_create.status_code == status.HTTP_201_CREATED
    loan_id = resp_create.data.get("id")
    assert resp_create.data.get("amount") == "500.00"
    assert resp_create.data.get("status") == "APPROVED"

    detail_url = reverse("loan-detail", args=[loan_id])
    resp_detail = auth_client.get(detail_url, format="json")
    assert resp_detail.status_code == status.HTTP_200_OK
    assert resp_detail.data.get("id") == loan_id
    assert resp_detail.data.get("amount") == "500.00"
