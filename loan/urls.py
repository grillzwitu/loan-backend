"""
Module: URL routing for loan application API endpoints.

Endpoints provided:
  - GET    /api/loan/               List loan applications
  - POST   /api/loan/               Create a new loan application
  - GET    /api/loan/{id}/          Retrieve a specific loan application
  - POST   /api/loan/{id}/withdraw/ Withdraw a pending loan application
"""
from typing import List
from django.urls import path, URLPattern
from .views import LoanApplicationListCreateView, LoanApplicationDetailView, LoanApplicationWithdrawView

urlpatterns: List[URLPattern] = [
    path('', LoanApplicationListCreateView.as_view(), name='loan-list-create'),
    path('<int:pk>/', LoanApplicationDetailView.as_view(), name='loan-detail'),
    path('<int:pk>/withdraw/', LoanApplicationWithdrawView.as_view(), name='loan-withdraw'),
]