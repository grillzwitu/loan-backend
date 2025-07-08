"""
Module: Caching integration tests for loan and fraud endpoints.

This module tests caching behaviors for:
  - Loan detail endpoint caching
  - Flagged loans list caching
  - Loan list endpoint caching
  - Loan dashboard endpoint caching
  - Serializer-level caching
"""

from typing import Any

import pytest
from django.core.cache import cache
from django.urls import reverse

from fraud.services import run_fraud_checks
from loan.models import LoanApplication


@pytest.mark.django_db
def test_loan_detail_caching(auth_client: Any, user: Any) -> None:
    """Test loan detail caching behavior.

    Args:
        auth_client (APIClient): Authenticated API client for regular user.
        user (User): Test user instance.

    Procedure:
        1. Create a loan and fetch its detail endpoint to populate cache.
        2. Update the loan status directly in the database.
        3. Fetch detail endpoint again to verify stale cached response.
        4. Clear cache and fetch detail endpoint to verify updated data.
    """
    # Step 1: Create and fetch loan detail to populate cache
    loan = LoanApplication.objects.create(user=user, amount=1000)
    url = reverse("loan-detail", args=(loan.pk,))
    response1 = auth_client.get(url, format="json")
    assert response1.status_code == 200
    data1 = response1.data
    # Step 2: Update loan status in database
    LoanApplication.objects.filter(pk=loan.pk).update(status="WITHDRAWN")
    # Step 3: Re-fetch loan detail to confirm stale cache
    response2 = auth_client.get(url, format="json")
    assert response2.data == data1
    # Step 4: Clear cache and fetch detail to verify status
    cache_key = f"loan_detail_{loan.pk}"
    cache.delete(cache_key)
    response3 = auth_client.get(url, format="json")
    assert response3.data["status"] == "WITHDRAWN"


@pytest.mark.django_db
def test_flagged_list_caching(admin_client: Any, user: Any) -> None:
    """Test flagged loans list caching behavior.

    Args:
        admin_client (APIClient): Authenticated admin client.
        user (User): Test user instance.

    Procedure:
        1. Create and flag an initial loan to populate cache.
        2. Fetch flagged list endpoint to cache results.
        3. Create and flag a second loan.
        4. Fetch flagged list endpoint again to confirm cached data.
        5. Clear cache and fetch to verify inclusion of new flagged loan.
    """
    # Step 1: Create and flag initial loan to populate flagged list
    loan1 = LoanApplication.objects.create(user=user, amount=6000000)
    run_fraud_checks(loan1)
    url = reverse("flagged-loans")
    response1 = admin_client.get(url, format="json")
    assert response1.status_code == 200
    data1 = response1.data
    # Step 2: Create and flag a second loan
    loan2 = LoanApplication.objects.create(user=user, amount=6000000)
    run_fraud_checks(loan2)
    # Step 3: Re-fetch flagged list to confirm stale cache
    response2 = admin_client.get(url, format="json")
    assert response2.data == data1
    # Step 4: Clear cache and fetch flagged list to verify new loan
    cache_key = "flagged_loans_page_1"
    cache.delete(cache_key)
    response3 = admin_client.get(url, format="json")
    ids = [item["id"] for item in response3.data["results"]]
    assert loan2.pk in ids


@pytest.mark.django_db
def test_loan_list_caching(auth_client: Any, user: Any) -> None:
    """Test user loan list caching behavior.

    Args:
        auth_client (APIClient): Authenticated API client for regular user.
        user (User): Test user instance.

    Procedure:
        1. Create initial loans and fetch loan list endpoint to populate cache.
        2. Create another loan to modify data.
        3. Fetch loan list endpoint again to confirm stale cached data.
        4. Clear cache and fetch endpoint to verify new loan appears.
    """
    # Step 1: Create initial loan applications
    for _ in range(2):
        LoanApplication.objects.create(user=user, amount=1000)
    url = reverse("loan-list-create")
    response1 = auth_client.get(url, format="json")
    assert response1.status_code == 200
    data1 = response1.data
    # Step 2: Create another loan
    LoanApplication.objects.create(user=user, amount=2000)
    # Step 3: Re-fetch loan list to confirm stale cache
    response2 = auth_client.get(url, format="json")
    assert response2.data == data1
    # Step 4: Clear cache and fetch loan list to verify new loan
    cache_key = f"loan_list.user_{user.pk}"
    cache.delete(cache_key)
    response3 = auth_client.get(url, format="json")
    assert response3.data["count"] == data1["count"] + 1


@pytest.mark.django_db
def test_loan_dashboard_caching(auth_client: Any, user: Any) -> None:
    """Test loan dashboard endpoint caching behavior.

    Args:
        auth_client (APIClient): Authenticated API client.
        user (User): Test user instance.

    Procedure:
        1. Create one loan for each status to set initial counts.
        2. Fetch dashboard endpoint to cache counts.
        3. Create an additional PENDING loan.
        4. Fetch again to confirm stale cached counts.
        5. Clear cache and fetch to verify updated counts.
    """
    # Step 1: Create one loan per status
    statuses = [choice[0] for choice in LoanApplication.STATUS_CHOICES]
    for status in statuses:
        LoanApplication.objects.create(user=user, amount=1000, status=status)
    url = reverse("loan-dashboard")
    response1 = auth_client.get(url, format="json")
    assert response1.status_code == 200
    data1 = response1.data
    # Step 2: Create an additional PENDING loan
    LoanApplication.objects.create(user=user, amount=2000)
    # Step 3: Re-fetch dashboard to confirm stale cache
    response2 = auth_client.get(url, format="json")
    assert response2.data == data1
    # Step 4: Clear cache and fetch dashboard to verify counts
    cache.delete("loan_dashboard")
    response3 = auth_client.get(url, format="json")
    assert response3.data["PENDING"] == data1["PENDING"] + 1


@pytest.mark.django_db
def test_serializer_caching(user: Any) -> None:
    """Test serializer-level caching for LoanApplication.

    Args:
        user (User): Test user instance.

    Procedure:
        1. Create a loan and clear serializer cache.
        2. Serialize instance to populate cache and record data.
        3. Update loan amount and serialize again to verify stale data.
        4. Clear cache and serialize to verify updated data is returned.
    """
    from loan.serializers import LoanApplicationSerializer

    # Step 1: Create loan instance
    loan = LoanApplication.objects.create(user=user, amount=1234)
    # Step 2: Clear serializer cache
    cache_key = f"serializer_loan_{loan.pk}"
    cache.delete(cache_key)
    # Step 3: Serialize loan to populate cache
    serializer1 = LoanApplicationSerializer(loan)
    data1 = serializer1.data
    # Step 4: Update loan amount to test stale cache
    LoanApplication.objects.filter(pk=loan.pk).update(amount=4321)
    serializer2 = LoanApplicationSerializer(
        LoanApplication.objects.get(pk=loan.pk)
    )
    data2 = serializer2.data
    assert data2 == data1
    # Step 5: Clear cache and re-serialize to verify updated data
    cache.delete(cache_key)
    serializer3 = LoanApplicationSerializer(
        LoanApplication.objects.get(pk=loan.pk)
    )
    data3 = serializer3.data
    assert data3["amount"] != data1["amount"]
