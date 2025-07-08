"""Module: Unit tests for caching behavior in fraud views."""

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIRequestFactory

from fraud.views import FlaggedLoanHistoryListView, FlaggedLoanListView

User = get_user_model()


@pytest.mark.django_db
def test_flagged_loan_list_view_cache_branch() -> None:
    """When cached data exists for flagged loan list, the view should return
    the cached data without querying the database."""
    admin = User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="pw",
        is_staff=True,
    )
    data = [{"id": 1, "dummy": "value"}]
    cache_key = "flagged_loans_page_1"
    cache.set(cache_key, data, 300)
    factory = APIRequestFactory()
    request = factory.get("/fraud/flagged/?page=1")
    request.user = admin
    view = FlaggedLoanListView.as_view()
    response = view(request)
    assert "results" in response.data and "count" in response.data
    assert response.data["results"] == data
    assert response.data["count"] == len(data)


@pytest.mark.django_db
def test_flagged_loan_history_view_cache_branch() -> None:
    """When cached data exists for flagged loan history list, the view should
    return the cached data without querying the database."""
    admin2 = User.objects.create_user(
        username="admin2",
        email="admin2@example.com",
        password="pw",
        is_staff=True,
    )
    history_data = [{"id": 2, "dummy": "old_value"}]
    cache_key = "flagged_loans_history_page_1"
    cache.set(cache_key, history_data, 300)
    factory2 = APIRequestFactory()
    request2 = factory2.get("/fraud/history/?page=1")
    request2.user = admin2
    view_history = FlaggedLoanHistoryListView.as_view()
    response2 = view_history(request2)
    assert "results" in response2.data and "count" in response2.data
    assert response2.data["results"] == history_data
    assert response2.data["count"] == len(history_data)


@pytest.mark.django_db
def test_flagged_loan_list_view_cache_branch_dict() -> None:
    """When cached data is a dict for list view, should return cached dict
    unchanged."""
    admin = User.objects.create_user(
        username="admind",
        email="admind@example.com",
        password="pw",
        is_staff=True
    )
    dict_data = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [{"id": 1, "dummy": "value"}],
    }
    cache_key = "flagged_loans_page_1"
    cache.set(cache_key, dict_data, 300)
    factory = APIRequestFactory()
    request = factory.get("/fraud/flagged/?page=1")
    request.user = admin
    view = FlaggedLoanListView.as_view()
    response = view(request)
    assert response.data == dict_data


@pytest.mark.django_db
def test_flagged_loan_history_view_cache_branch_dict() -> None:
    """When cached data is a dict for history view, should return cached dict
    unchanged."""
    admin2 = User.objects.create_user(
        username="admin2d",
        email="admin2d@example.com",
        password="pw",
        is_staff=True
    )
    dict_data = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [{"id": 2, "dummy": "old_value"}],
    }
    cache_key = "flagged_loans_history_page_1"
    cache.set(cache_key, dict_data, 300)
    factory2 = APIRequestFactory()
    request2 = factory2.get("/fraud/history/?page=1")
    request2.user = admin2
    view_history = FlaggedLoanHistoryListView.as_view()
    response2 = view_history(request2)
    assert response2.data == dict_data
