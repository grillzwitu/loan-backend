"""Module: Unit tests for LoanApplicationWithdrawView branch coverage."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIRequestFactory

from loan.models import LoanApplication
from loan.views_impl.actions import LoanApplicationWithdrawView

User = get_user_model()


@pytest.mark.django_db
def test_withdraw_other_user_forbidden() -> None:
    """Attempting to withdraw a loan by a non-owner should return 403
    FORBIDDEN."""
    owner = User.objects.create_user(
        username="owner", email="owner@example.com", password="password"
    )
    other = User.objects.create_user(
        username="other", email="other@example.com", password="password"
    )
    loan = LoanApplication.objects.create(
        user=owner,
        amount="500.00",
        purpose="Test"
    )
    factory = APIRequestFactory()
    request = factory.post(f"/loans/{loan.pk}/withdraw/")
    request.user = other

    view = LoanApplicationWithdrawView.as_view()
    response = view(request, pk=loan.pk)
    assert response.status_code == status.HTTP_403_FORBIDDEN
