"""
Module: Ensure each view class can be resolved and
as_view() returns a callable.
"""

import pytest

from loan import views


@pytest.mark.parametrize(
    "view_class",
    [
        views.LoanApplicationListCreateView,
        views.LoanApplicationDetailView,
        views.LoanApplicationWithdrawView,
        views.LoanApplicationApproveView,
        views.LoanApplicationRejectView,
        views.LoanApplicationFlagView,
        views.LoanDashboardView,
    ],
)
@pytest.mark.django_db
def test_views_as_view_callable(view_class: type) -> None:
    """
    Test that as_view() for each view class returns
    a callable withouterror.
    """

    view_fn = view_class.as_view()
    assert callable(view_fn)
