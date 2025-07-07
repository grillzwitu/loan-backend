"""Module: Unit tests for recent loans rule in fraud.services."""

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache

from fraud.models import FraudFlag
from fraud.services import run_fraud_checks
from loan.models import LoanApplication

User = get_user_model()


@pytest.mark.django_db
def test_run_fraud_checks_flags_many_recent_loans() -> None:
    """
    run_fraud_checks should flag when more than 3 loans exist in the
    past 24 hours.
    """
    cache.clear()
    user = User.objects.create_user(
        username="recentuser", email="recent@example.com", password="password"
    )
    # create 3 loans (no flags)
    for _ in range(3):
        loan = LoanApplication.objects.create(user=user, amount=1000)
        reasons = run_fraud_checks(loan)
        assert "More than 3 loans in 24 hours" not in reasons
    # 4th loan should trigger flag
    loan4 = LoanApplication.objects.create(user=user, amount=1000)
    reasons4 = run_fraud_checks(loan4)
    assert "More than 3 loans in 24 hours" in reasons4
    flags = FraudFlag.objects.filter(loan=loan4, reason="More than 3 loans in 24 hours")
    assert flags.exists()
    loan4.refresh_from_db()
    assert loan4.status == "FLAGGED"
