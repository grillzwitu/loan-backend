from typing import Any

import pytest
from django.contrib.auth import get_user_model

from fraud.models import FraudFlag
from loan.models import LoanApplication

User: Any = get_user_model()


@pytest.mark.django_db
def test_withdraw_pending_loan() -> None:
    """The withdraw method should set status to WITHDRAWN for pending loans."""
    user = User.objects.create_user(
        username="user7",
        email="user7@example.com",
        password="password",
    )
    loan = LoanApplication.objects.create(user=user, amount=1000)
    loan.withdraw()
    loan.refresh_from_db()
    assert loan.status == "WITHDRAWN"


@pytest.mark.django_db
def test_withdraw_non_pending_loan_raises() -> None:
    """The withdraw method should raise ValueError when loan is not pending or
    flagged."""
    user = User.objects.create_user(
        username="user8",
        email="user8@example.com",
        password="password",
    )
    loan = LoanApplication.objects.create(user=user, amount=1000)
    loan.status = "APPROVED"
    loan.save(update_fields=["status"])
    with pytest.raises(ValueError):
        loan.withdraw()


@pytest.mark.django_db
def test_withdraw_flagged_loan() -> None:
    """The withdraw method should set status to WITHDRAWN for flagged loans,
    and preserve existing FraudFlag records."""
    user = User.objects.create_user(
        username="user9",
        email="user9@example.com",
        password="password",
    )
    loan = LoanApplication.objects.create(user=user, amount=500)
    FraudFlag.objects.create(loan=loan, reason="fraud check failed")
    loan.status = "FLAGGED"
    loan.save(update_fields=["status"])
    loan.withdraw()
    loan.refresh_from_db()
    assert loan.status == "WITHDRAWN"
    assert loan.fraud_flags.count() == 1
