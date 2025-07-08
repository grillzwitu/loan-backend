import pytest
from django.contrib.auth import get_user_model

from fraud.models import FraudFlag
from fraud.services import run_fraud_checks
from loan.models import LoanApplication

User = get_user_model()


@pytest.mark.django_db
def test_run_fraud_checks_flags_high_amount() -> None:
    """run_fraud_checks should flag loans whose amount exceeds threshold."""
    user = User.objects.create_user(
        username="user1", email="user1@example.com", password="password"
    )
    # Use amount above the threshold of 5,000,000 to trigger fraud flag
    loan = LoanApplication.objects.create(user=user, amount=6000000)
    reasons = run_fraud_checks(loan)
    assert reasons == ["Amount exceeds threshold"]
    flags = FraudFlag.objects.filter(loan=loan)
    assert flags.count() == 1
    flag = flags.first()
    assert flag is not None
    assert flag.reason == "Amount exceeds threshold"


@pytest.mark.django_db
def test_run_fraud_checks_no_flags_for_low_amount() -> None:
    """run_fraud_checks should not flag loans whose amount is below
    threshold."""
    user = User.objects.create_user(
        username="user2", email="user2@example.com", password="password"
    )
    loan = LoanApplication.objects.create(user=user, amount=1000)
    reasons = run_fraud_checks(loan)
    assert reasons == []
    assert not FraudFlag.objects.filter(loan=loan).exists()
