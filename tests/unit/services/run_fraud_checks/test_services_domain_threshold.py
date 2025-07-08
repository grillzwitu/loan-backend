"""
Module: Unit tests for fraud.services domain user threshold.

Ensures that loans are flagged starting at the 11th user sharing same
email domain.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache

from loan.models import LoanApplication
from fraud.services import run_fraud_checks
from fraud.models import FraudFlag

User = get_user_model()


@pytest.mark.django_db
def test_domain_threshold_flags_on_eleventh_user() -> None:
    """
    run_fraud_checks should flag the 11th loan when more than 10 users
    use the same email domain. Earlier loans must not be flagged.
    """
    cache.clear()
    domain: str = "example.com"

    # Create 10 users with the same domain and assert no flag
    for i in range(1, 11):
        user = User.objects.create_user(
            username=f"user{i}", email=f"user{i}@{domain}", password="pw"
        )
        loan = LoanApplication.objects.create(user=user, amount=1000)
        reasons = run_fraud_checks(loan)
        assert "Email domain used by more than 10 users" not in reasons
        loan.refresh_from_db()
        # Loans should be auto-approved (amount <= 1_000_000)
        assert loan.status == "APPROVED"

    # Clear cache so domain count is recomputed for the 11th user
    cache.clear()

    # 11th user should trigger the domain threshold rule
    user11 = User.objects.create_user(
        username="user11", email=f"user11@{domain}", password="pw"
    )
    loan11 = LoanApplication.objects.create(user=user11, amount=1000)
    reasons11 = run_fraud_checks(loan11)
    # Should flag for domain usage rule
    assert "Email domain used by more than 10 users" in reasons11
    loan11.refresh_from_db()
    assert loan11.status == "FLAGGED"
    # FraudFlag record must exist
    assert FraudFlag.objects.filter(
        loan=loan11, reason="Email domain used by more than 10 users"
    ).exists()
