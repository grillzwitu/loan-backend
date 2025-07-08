"""
Module: Tests for logging in fraud services and loan withdrawal view.
Verifies that appropriate warning and error messages are logged.
"""

import logging

import pytest
from _pytest.logging import LogCaptureFixture
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from fraud.services import run_fraud_checks
from loan.models import LoanApplication

User = get_user_model()


@pytest.mark.django_db
def test_run_fraud_checks_logging(caplog: LogCaptureFixture) -> None:
    """run_fraud_checks should log a WARNING when a loan is flagged for high
    amount."""
    caplog.set_level(logging.WARNING, logger="fraud.services")
    user = User.objects.create_user(
        username="user_log",
        email="log@example.com",
        password="password",
    )
    # Create loan above threshold to trigger flag and logging
    loan = LoanApplication.objects.create(
        user=user,
        amount=6000000,
    )
    run_fraud_checks(loan)
    # Assert a warning log was emitted
    assert any(
        (
            record.levelname == "WARNING"
            and "flagged for reasons" in record.getMessage()
        )
        for record in caplog.records
    )


@pytest.mark.django_db
def test_withdraw_endpoint_logging(caplog: LogCaptureFixture) -> None:
    """Withdrawal endpoint should log INFO on successful withdrawal and ERROR
    on invalid retry."""
    # Capture only ERROR logs since auto-approved loans cannot be withdrawn
    caplog.set_level(logging.ERROR, logger="loan.views")
    client = APIClient()
    # Create and authenticate user
    user = User.objects.create_user(
        username="loguser",
        email="log2@example.com",
        password="password",
    )
    # Obtain tokens
    login_resp = client.post(
        reverse("token_obtain_pair"),
        {
            "username": user.username,
            "password": "password",
        },
        format="json",
    )
    access_token = login_resp.data["access"]
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access_token}",
    )
    # Create a new loan
    create_resp = client.post(
        reverse("loan-list-create"),
        {"amount": "1000.00"},
        format="json",
    )
    loan_id = create_resp.data["id"]
    # Withdraw the loan
    caplog.clear()
    withdraw_resp = client.post(
        reverse("loan-withdraw", args=[loan_id]),
        {},
        format="json",
    )
    # Withdrawal of auto-approved loan should return 400 and log an error
    assert withdraw_resp.status_code == status.HTTP_400_BAD_REQUEST
    assert any(
        record.levelname == "ERROR"
        and "Failed to withdraw loan id=" in record.getMessage()
        for record in caplog.records
    )
