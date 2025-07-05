import pytest
from django.contrib.auth import get_user_model
from loan.models import LoanApplication
from fraud.models import FraudFlag

User = get_user_model()

@pytest.mark.django_db
def test_loan_string_representation():
    """
    The __str__ method of LoanApplication should return the correct formatted string.
    """
    user = User.objects.create_user(username="user1", email="user1@example.com", password="password")
    loan = LoanApplication.objects.create(user=user, amount=100)
    expected = f"Loan {loan.id} - {user}"
    assert str(loan) == expected

@pytest.mark.django_db
def test_fraudflag_string_representation():
    """
    The __str__ method of FraudFlag should return the correct formatted string.
    """
@pytest.mark.django_db
def test_withdraw_pending_loan():
    """
    The withdraw method should set status to WITHDRAWN for pending loans.
    """
    user = User.objects.create_user(username="user3", email="user3@example.com", password="password")
    loan = LoanApplication.objects.create(user=user, amount=1000)
    loan.withdraw()
    loan.refresh_from_db()
    assert loan.status == "WITHDRAWN"

@pytest.mark.django_db
def test_withdraw_non_pending_loan_raises():
    """
    The withdraw method should raise ValueError when loan is not pending.
    """
    user = User.objects.create_user(username="user4", email="user4@example.com", password="password")
    loan = LoanApplication.objects.create(user=user, amount=1000)
    loan.status = "APPROVED"
    loan.save(update_fields=["status"])
    with pytest.raises(ValueError):
        loan.withdraw()
    user = User.objects.create_user(username="user2", email="user2@example.com", password="password")
    loan = LoanApplication.objects.create(user=user, amount=100)
    flag = FraudFlag.objects.create(loan=loan, reason="suspicious activity")
    expected = f"Flag {flag.id} - {loan}"
    assert str(flag) == expected