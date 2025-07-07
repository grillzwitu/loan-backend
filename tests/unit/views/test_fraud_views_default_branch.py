"""Module: Unit tests for default (non-cache) branches in fraud views."""

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIRequestFactory

from fraud.models import FraudFlag
from fraud.views import FlaggedLoanHistoryListView, FlaggedLoanListView
from loan.models import LoanApplication

User = get_user_model()


@pytest.mark.django_db
def test_flagged_loan_list_view_default_branch() -> None:
    """
    When no cache exists and flagged loans exist in the database,
    FlaggedLoanListView should query the DB and return the list of flagged loans.
    """
    cache.clear()
    admin = User.objects.create_user(
        username="admin_default",
        email="admin_default@example.com",
        password="pw",
        is_staff=True,
    )
    normal_user = User.objects.create_user(
        username="normal", email="normal@example.com", password="pw"
    )
    # Create a flagged loan
    loan = LoanApplication.objects.create(
        user=normal_user, amount=100.00, status="FLAGGED"
    )
    factory = APIRequestFactory()
    request = factory.get("/fraud/flagged/?page=1")
    request.user = admin

    view = FlaggedLoanListView.as_view()
    response = view(request)
    assert "results" in response.data and "count" in response.data
    assert response.data["results"] and response.data["results"][0]["id"] == loan.id


@pytest.mark.django_db
def test_flagged_loan_history_view_default_branch() -> None:
    """
    When no cache exists and a loan has historical fraud flags,
    FlaggedLoanHistoryListView should query the DB and return flagged loan history.
    """
    cache.clear()
    admin2 = User.objects.create_user(
        username="admin_history",
        email="admin_history@example.com",
        password="pw",
        is_staff=True,
    )
    user2 = User.objects.create_user(
        username="user_history", email="user_history@example.com", password="pw"
    )
    # Create a loan and a fraud flag (history)
    loan2 = LoanApplication.objects.create(user=user2, amount=200.00)
    FraudFlag.objects.create(loan=loan2, reason="Test history flag")

    factory2 = APIRequestFactory()
    request2 = factory2.get("/fraud/history/?page=1")
    request2.user = admin2

    view_history = FlaggedLoanHistoryListView.as_view()
    response2 = view_history(request2)
    assert "results" in response2.data and "count" in response2.data
    assert response2.data["results"] and response2.data["results"][0]["id"] == loan2.id
