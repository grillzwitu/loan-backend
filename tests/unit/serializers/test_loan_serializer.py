"""Module: LoanApplicationSerializer unit tests for creation and caching.

This module contains unit tests to ensure that:
- The serializer's create method correctly associates the request user
  and populates validated fields.
- The to_representation method caches output on first serialization,
  and returns cached data on subsequent accesses even if the instance changes.
"""

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIRequestFactory

from loan.models import LoanApplication
from loan.serializers import LoanApplicationSerializer

User = get_user_model()


@pytest.mark.django_db
def test_serializer_create_assigns_user_and_fields():
    """Verify that serializer.create method assigns the request user to the new
    LoanApplication and sets amount and purpose correctly."""
    user = User.objects.create_user(
        username="serializer_user",
        email="serializer@example.com",
        password="password",
    )
    factory = APIRequestFactory()
    request = factory.post(
        "/loans/",
        {"amount": "1500.00", "purpose": "Test Loan Purpose"},
        format="json",
    )
    request.user = user
    data = {"amount": "1500.00", "purpose": "Test Loan Purpose"}
    serializer = LoanApplicationSerializer(
        data=data,
        context={"request": request}
    )
    assert serializer.is_valid(), serializer.errors
    loan = serializer.save()
    assert loan.user == user
    assert loan.amount == Decimal("1500.00")
    assert loan.purpose == "Test Loan Purpose"


@pytest.mark.django_db
def test_to_representation_caches_output():
    """
    Ensure that to_representation caches the serialized data in Django cache
    and returns the cached representation on subsequent calls, even if the
    LoanApplication instance is updated.
    """
    cache.clear()
    user = User.objects.create_user(
        username="cache_user",
        email="cache@example.com",
        password="password",
    )
    loan = LoanApplication.objects.create(
        user=user,
        amount=Decimal("200.00"),
        purpose="Cache Test",
    )
    serializer = LoanApplicationSerializer(loan)
    cache_key = f"serializer_loan_{loan.pk}"
    assert cache.get(cache_key) is None
    first_data = serializer.data
    assert cache.get(cache_key) == first_data
    loan.amount = Decimal("300.00")
    loan.save()
    second_data = serializer.data
    assert second_data == first_data
