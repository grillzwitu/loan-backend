"""
Module: URL routing for loan application API endpoints.

Defines URL patterns for loan operations (list/create, retrieve).
"""
from typing import List
from django.urls import path, URLPattern
from .views import LoanApplicationListCreateView, LoanApplicationDetailView, LoanApplicationWithdrawView

urlpatterns: List[URLPattern] = [
    path('', LoanApplicationListCreateView.as_view(), name='loan-list-create'),
    path('<int:pk>/', LoanApplicationDetailView.as_view(), name='loan-detail'),
    path('<int:pk>/withdraw/', LoanApplicationWithdrawView.as_view(), name='loan-withdraw'),
]