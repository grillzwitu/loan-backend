import pytest
from django.contrib.auth import get_user_model
from loan.models import LoanApplication
from fraud.models import FraudFlag
from fraud.services import run_fraud_checks

User = get_user_model()

@pytest.mark.django_db
def test_run_fraud_checks_flags_high_amount() -> None:
    """
    run_fraud_checks should flag loans whose amount exceeds threshold.
    """
    user = User.objects.create_user(username="user1", email="user1@example.com", password="password")
    # Use amount above the threshold of 5,000,000 to trigger fraud flag
    loan = LoanApplication.objects.create(user=user, amount=6000000)
    reasons = run_fraud_checks(loan)
    assert reasons == ["Amount exceeds threshold"]
    flags = FraudFlag.objects.filter(loan=loan)
    assert flags.count() == 1
    assert flags.first().reason == "Amount exceeds threshold"

@pytest.mark.django_db
def test_run_fraud_checks_no_flags_for_low_amount() -> None:
    """
    run_fraud_checks should not flag loans whose amount is below threshold.
    """
    user = User.objects.create_user(username="user2", email="user2@example.com", password="password")
    loan = LoanApplication.objects.create(user=user, amount=1000)
    reasons = run_fraud_checks(loan)
    assert reasons == []
    assert not FraudFlag.objects.filter(loan=loan).exists()

@pytest.mark.django_db
def test_run_fraud_checks_flags_many_recent_loans() -> None:
    """
    run_fraud_checks should flag when more than 3 loans exist in the past 24 hours.
    """
    user = User.objects.create_user(username="user3", email="user3@example.com", password="password")
    # First three loans: no flags
    for _ in range(3):
        loan = LoanApplication.objects.create(user=user, amount=1000)
        reasons = run_fraud_checks(loan)
        assert reasons == []
    # Fourth loan should trigger flag
    loan4 = LoanApplication.objects.create(user=user, amount=1000)
    reasons = run_fraud_checks(loan4)
    assert "More than 3 loans in 24 hours" in reasons
    flags = FraudFlag.objects.filter(loan=loan4, reason="More than 3 loans in 24 hours")
    assert flags.exists()
    loan4.refresh_from_db()
    assert loan4.status == "FLAGGED"

@pytest.mark.django_db
def test_run_fraud_checks_flags_many_users_same_domain() -> None:
    """
    run_fraud_checks should flag when email domain is used by more than 10 users.
    """
    # Create 11 users with same domain
    for i in range(11):
        User.objects.create_user(username=f"user{i}", email=f"user{i}@domain.com", password="password")
    user = User.objects.get(username="user0")
    loan = LoanApplication.objects.create(user=user, amount=1000)
    reasons = run_fraud_checks(loan)
    assert "Email domain used by more than 10 users" in reasons
    flags = FraudFlag.objects.filter(loan=loan, reason="Email domain used by more than 10 users")
    assert flags.exists()
    loan.refresh_from_db()
    assert loan.status == "FLAGGED"