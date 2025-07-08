import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate

from fraud.models import FraudFlag
from fraud.views import FlaggedLoanHistoryListView
from loan.models import LoanApplication

User = get_user_model()


@pytest.mark.django_db
def test_flagged_history_view_get_queryset() -> None:
    """The FlaggedLoanHistoryListView.get_queryset should filter loans with any
    FraudFlag records, regardless of current status."""
    # Create a staff user and authenticate
    staff_user = User.objects.create_user(
        username="staff", password="pass", is_staff=True
    )
    # Create two loans: one flagged, one not flagged
    loan_flagged = LoanApplication.objects.create(user=staff_user, amount=150)
    FraudFlag.objects.create(loan=loan_flagged, reason="test reason")
    loan_not_flagged = LoanApplication.objects.create(
        user=staff_user,
        amount=250
    )
    # Prepare the view and request
    view = FlaggedLoanHistoryListView()
    factory = APIRequestFactory()
    request = factory.get("/api/fraud/flagged/all/")
    force_authenticate(request, user=staff_user)
    view.request = request
    # Fetch queryset and assert only the flagged loan is included
    qs = view.get_queryset()
    assert loan_flagged in qs
    assert loan_not_flagged not in qs
    assert list(qs) == [loan_flagged]
