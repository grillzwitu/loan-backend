"""
Module: Model-level tests for the FraudFlag model.
Verifies relationship, string representation, and timestamp behavior.
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from loan.models import LoanApplication
from fraud.models import FraudFlag

User = get_user_model()

@pytest.mark.django_db
def test_fraudflag_related_name_and_str() -> None:
    """
    Ensure FraudFlag is accessible via loan.fraud_flags and __str__ is correct.
    """
    user = User.objects.create_user(
        username="flaguser", email="flag@example.com", password="password"
    )
    loan = LoanApplication.objects.create(user=user, amount=500)
    flag = FraudFlag.objects.create(loan=loan, reason="Test reason")
    # Relationship via related_name
    flags_for_loan = list(loan.fraud_flags.all())
    assert flag in flags_for_loan
    # String representation
    expected_str = f"Flag {flag.id} - {loan}"
    assert str(flag) == expected_str

@pytest.mark.django_db
def test_fraudflag_timestamp_auto_now_add() -> None:
    """
    Verify that flagged_at is automatically set to the current time upon creation.
    """
    user = User.objects.create_user(
        username="timeuser", email="time@example.com", password="password"
    )
    loan = LoanApplication.objects.create(user=user, amount=1000)
    before = timezone.now()
    flag = FraudFlag.objects.create(loan=loan, reason="Timestamp test")
    after = timezone.now()
    # flagged_at should be between before and after timestamps
    assert before <= flag.flagged_at <= after