"""Module: Unit tests for loan.views facade.

Ensures that the facade module re-exports all view classes expected by the API.
"""

import pytest

import loan.views as views


@pytest.mark.parametrize(
    "view_name",
    [
        "LoanApplicationListCreateView",
        "LoanApplicationDetailView",
        "LoanApplicationWithdrawView",
        "LoanApplicationApproveView",
        "LoanApplicationRejectView",
        "LoanApplicationFlagView",
        "LoanDashboardView",
    ],
)
@pytest.mark.django_db
def test_facade_exports_all_views(view_name: str) -> None:
    """Verify that the loan.views module exposes the expected view classes."""
    assert hasattr(views, view_name), f"{view_name} not found in loan.views"
