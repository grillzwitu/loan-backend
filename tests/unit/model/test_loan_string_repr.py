from typing import Any

import pytest
from django.contrib.auth import get_user_model

from loan.models import LoanApplication

User: Any = get_user_model()


@pytest.mark.django_db
def test_loan_string_representation() -> None:
    """The __str__ method of LoanApplication should return the correct
    formatted string."""
    user = User.objects.create_user(
        username="user1",
        email="user1@example.com",
        password="password",
    )
    loan = LoanApplication.objects.create(
        user=user,
        amount=100,
    )
    expected = f"Loan {loan.id} - {user}"
    assert str(loan) == expected
