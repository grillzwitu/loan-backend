import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache

from fraud.models import FraudFlag
from fraud.services import run_fraud_checks
from loan.models import LoanApplication

User = get_user_model()


@pytest.mark.django_db
def test_run_fraud_checks_flags_many_users_same_domain() -> None:
    # Clear cache to ensure domain_user_count branch executes
    cache.clear()
    """
    run_fraud_checks should flag when email domain is used by more than
    10 users.
    """
    # Clear cache to ensure domain_user_count branch executes
    cache.clear()
    # Create 11 users with same domain
    for i in range(11):
        User.objects.create_user(
            username=f"user{i}",
            email=f"user{i}@domain.com",
            password="password",
        )
    user = User.objects.get(username="user0")
    loan = LoanApplication.objects.create(user=user, amount=1000)
    reasons = run_fraud_checks(loan)
    assert "Email domain used by more than 10 users" in reasons
    flags = FraudFlag.objects.filter(
        loan=loan, reason="Email domain used by more than 10 users"
    )
    assert flags.exists()
    loan.refresh_from_db()
    assert loan.status == "FLAGGED"
