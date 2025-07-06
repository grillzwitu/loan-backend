import pytest
from django.contrib.auth import get_user_model
from loan.models import LoanApplication
from fraud.models import FraudFlag

from django.db.models.signals import post_save
from fraud.signals import loan_post_save
from loan.models import LoanApplication

# Disable post_save fraud checks for LoanApplication so withdraw logic can be tested
post_save.disconnect(receiver=loan_post_save, sender=LoanApplication)

User = get_user_model()

@pytest.mark.django_db
def test_loan_string_representation() -> None:
    """
    The __str__ method of LoanApplication should return the correct formatted string.
    """
    user = User.objects.create_user(
        username="user1", email="user1@example.com", password="password"
    )
    loan = LoanApplication.objects.create(user=user, amount=100)
    expected = f"Loan {loan.id} - {user}"
    assert str(loan) == expected

@pytest.mark.django_db
def test_fraudflag_string_representation() -> None:
    """
    The __str__ method of FraudFlag should return the correct formatted string.
    """
    user = User.objects.create_user(
        username="user2", email="user2@example.com", password="password"
    )
    loan = LoanApplication.objects.create(user=user, amount=100)
    flag = FraudFlag.objects.create(loan=loan, reason="test reason")
    expected = f"Flag {flag.id} - {loan}"
    assert str(flag) == expected

@pytest.mark.django_db
def test_withdraw_pending_loan() -> None:
    """
    The withdraw method should set status to WITHDRAWN for pending loans.
    """
    user = User.objects.create_user(
        username="user3", email="user3@example.com", password="password"
    )
    loan = LoanApplication.objects.create(user=user, amount=1000)
    loan.withdraw()
    loan.refresh_from_db()
    assert loan.status == "WITHDRAWN"

@pytest.mark.django_db
def test_withdraw_non_pending_loan_raises() -> None:
    """
    The withdraw method should raise ValueError when loan is not pending.
    """
    user = User.objects.create_user(
        username="user4", email="user4@example.com", password="password"
    )
    loan = LoanApplication.objects.create(user=user, amount=1000)
    # Change status to a non-pending value
    loan.status = "APPROVED"
    loan.save(update_fields=["status"])
    with pytest.raises(ValueError):
        loan.withdraw()