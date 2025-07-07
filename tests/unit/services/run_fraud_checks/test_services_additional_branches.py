"""Module: Additional unit tests for fraud services run_fraud_checks branch coverage."""

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache

from fraud.models import FraudFlag
from fraud.services import run_fraud_checks
from loan.models import LoanApplication

User = get_user_model()


@pytest.mark.django_db
def test_auto_approve_small_amount() -> None:
    """
    run_fraud_checks should auto-approve loans with no flags and amount <=1,000,000.
    """
    cache.clear()
    user = User.objects.create_user(
        username="user_auto", email="auto@example.com", password="pw"
    )
    loan = LoanApplication.objects.create(user=user, amount=500000)
    reasons = run_fraud_checks(loan)
    assert reasons == []
    loan.refresh_from_db()
    assert loan.status == "APPROVED"


@pytest.mark.django_db
def test_recent_loans_no_flag_for_few_loans() -> None:
    """
    run_fraud_checks should not flag when user has <=3 loans in 24 hours.
    """
    cache.clear()
    user = User.objects.create_user(
        username="user_recent", email="recent@example.com", password="pw"
    )
    last_loan = None
    for _ in range(3):
        loan = LoanApplication.objects.create(user=user, amount=1000)
        reasons = run_fraud_checks(loan)
        assert reasons == []
        assert not FraudFlag.objects.filter(loan=loan).exists()
        last_loan = loan
    # Status should be APPROVED after three loans
    assert last_loan.status == "APPROVED"


@pytest.mark.django_db
def test_domain_user_count_cache_hits_branch() -> None:
    """
    run_fraud_checks should use cached domain user count on subsequent calls.
    """
    cache.clear()
    test_domain = "cacheddomain.com"
    # Create 11 users with the same domain
    for i in range(11):
        User.objects.create_user(
            username=f"cd{i}", email=f"cd{i}@{test_domain}", password="pw"
        )
    # First run to populate cache for domain count
    primary_user = User.objects.filter(email__endswith=test_domain).first()
    loan1 = LoanApplication.objects.create(user=primary_user, amount=1000)
    reasons1 = run_fraud_checks(loan1)
    assert "Email domain used by more than 10 users" in reasons1
    # Second run should hit cache and still flag without recalculating
    second_user = User.objects.filter(email__endswith=test_domain).last()
    loan2 = LoanApplication.objects.create(user=second_user, amount=1000)
    # Manually set a wrong count to test cache usage
    cache.set(f"fraud.domain_user_count_{test_domain}", 5, 300)
    reasons2 = run_fraud_checks(loan2)
    # Using cached value 5 (<10) should not flag
    assert "Email domain used by more than 10 users" not in reasons2
    # Loan2 should be auto-approved since no fraud flags
    loan2.refresh_from_db()
    assert loan2.status == "APPROVED"
