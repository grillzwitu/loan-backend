"""
Module: API views for fraud app, handling flagged loan endpoints.
"""

import logging
from django.db.models.query import QuerySet

from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from loan.models import LoanApplication

from .serializers import FlaggedLoanSerializer

logger: logging.Logger = logging.getLogger(__name__)


class FlaggedLoanListView(generics.ListAPIView):
    """
    List all flagged LoanApplication instances.
    Admin users only.
    """

    permission_classes = (IsAdminUser,)
    serializer_class = FlaggedLoanSerializer

    def get_queryset(self) -> QuerySet[LoanApplication]:
        """
        Return queryset of loans flagged for fraud.
        """
        return LoanApplication.objects.filter(status="FLAGGED").order_by("id")
