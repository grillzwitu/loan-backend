"""
Module: URL routing for fraud-related API endpoints.

Endpoints:
- GET /fraud/flagged/ (name='flagged-loans'):
    List all currently flagged loans for admin users. Returns a paginated response with `count`, `next`, `previous`, and `results` fields.
- GET /fraud/flagged/all/ (name='flagged-loans-history'):
    List all loans that have ever been flagged for fraud, regardless of current status. Returns a paginated response with `count`, `next`, `previous`, and `results` fields.
"""

from typing import List

from django.urls import URLPattern, path

from .views import FlaggedLoanHistoryListView, FlaggedLoanListView

urlpatterns: List[URLPattern] = [
    path("flagged/", FlaggedLoanListView.as_view(), name="flagged-loans"),
    path(
        "flagged/all/",
        FlaggedLoanHistoryListView.as_view(),
        name="flagged-loans-history",
    ),
]
