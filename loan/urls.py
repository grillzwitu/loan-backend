"""
Module: URL routing for loan application API endpoints, including admin actions.

Endpoints provided:
  - GET    /api/loan/               List loan applications
  - POST   /api/loan/               Create a new loan application
  - GET    /api/loan/{id}/          Retrieve a specific loan application
  - POST   /api/loan/{id}/withdraw/ Withdraw a pending loan application
  - POST   /api/loan/{id}/approve/  Approve a pending or flagged loan application (admin)
  - POST   /api/loan/{id}/reject/   Reject a pending or flagged loan application (admin)
  - POST   /api/loan/{id}/flag/     Flag a pending loan application (admin)
"""
from typing import List
from django.urls import path, URLPattern
from .views import LoanApplicationListCreateView, LoanApplicationDetailView, LoanApplicationWithdrawView, LoanApplicationApproveView, LoanApplicationRejectView, LoanApplicationFlagView

urlpatterns: List[URLPattern] = [
    path('', LoanApplicationListCreateView.as_view(), name='loan-list-create'),
    path('<int:pk>/', LoanApplicationDetailView.as_view(), name='loan-detail'),
    path('<int:pk>/withdraw/', LoanApplicationWithdrawView.as_view(), name='loan-withdraw'),
    path('<int:pk>/approve/', LoanApplicationApproveView.as_view(), name='loan-approve'),
    path('<int:pk>/reject/', LoanApplicationRejectView.as_view(), name='loan-reject'),
    path('<int:pk>/flag/', LoanApplicationFlagView.as_view(), name='loan-flag'),
]