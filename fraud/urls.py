"""
Module: URL routing for fraud-related API endpoints.
"""
from typing import List
from django.urls import path, URLPattern

from .views import FlaggedLoanListView

urlpatterns: List[URLPattern] = [
    path('flagged/', FlaggedLoanListView.as_view(), name='flagged-loans'),
]