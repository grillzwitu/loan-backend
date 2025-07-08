import pytest
from django.contrib.auth import get_user_model

from fraud.services import run_fraud_checks
from loan.models import LoanApplication

User = get_user_model()


@pytest.mark.django_db
def test_run_fraud_checks_keeps_high_value_pending() -> None:
    """run_fraud_checks should keep loans >1,000,000 pending for admin review
    when no other fraud flags."""
    user = User.objects.create_user(
        username="highuser", email="high@example.com", password="password"
    )
    loan = LoanApplication.objects.create(user=user, amount=2000000)
    reasons = run_fraud_checks(loan)
    assert reasons == []
    loan.refresh_from_db()
    assert loan.status == "PENDING"
