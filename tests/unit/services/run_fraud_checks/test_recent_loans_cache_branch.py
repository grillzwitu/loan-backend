"""Module: Unit test for recent loans fraud rule with cache behavior."""

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache

from fraud.models import FraudFlag
from fraud.services import run_fraud_checks
from loan.models import LoanApplication

User = get_user_model()


@pytest.mark.django_db
def test_run_fraud_checks_flags_many_loans_after_cache_clear() -> None:
    """run_fraud_checks should flag when more than 3 loans exist in the past 24
    hours after clearing cache."""
    cache.clear()
    user = User.objects.create_user(
        username="recent_cache_user", email="rcu@example.com", password="pw"
    )
    # Create 4 loans quickly
    loans = [
        LoanApplication.objects.create(user=user, amount=1000)
        for _ in range(4)
    ]
    last_loan = loans[-1]
    reasons = run_fraud_checks(last_loan)
    assert "More than 3 loans in 24 hours" in reasons
    flags = FraudFlag.objects.filter(
        loan=last_loan, reason="More than 3 loans in 24 hours"
    )
    assert flags.exists()
    last_loan.refresh_from_db()
    assert last_loan.status == "FLAGGED"
