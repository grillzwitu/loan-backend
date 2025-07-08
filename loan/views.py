"""
Facade for loan views: re-export implementations from loan.views_impl
"""

from loan.views_impl.actions import (LoanApplicationApproveView,
                                     LoanApplicationFlagView,
                                     LoanApplicationRejectView,
                                     LoanApplicationWithdrawView)
from loan.views_impl.dashboard import LoanDashboardView
from loan.views_impl.detail import LoanApplicationDetailView
from loan.views_impl.list_create import LoanApplicationListCreateView

__all__ = [
    "LoanApplicationListCreateView",
    "LoanApplicationDetailView",
    "LoanApplicationWithdrawView",
    "LoanApplicationApproveView",
    "LoanApplicationRejectView",
    "LoanApplicationFlagView",
    "LoanDashboardView",
]
