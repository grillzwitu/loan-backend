"""
Module: API views for fraud app, handling flagged loan endpoints.
"""
import logging
from typing import Any, List
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from loan.serializers import LoanApplicationSerializer
from .serializers import FlaggedLoanSerializer
from loan.models import LoanApplication

logger: logging.Logger = logging.getLogger(__name__)

class FlaggedLoanListView(generics.ListAPIView):
    """
    List all flagged LoanApplication instances.
    Admin users only.
    """
    permission_classes = (IsAdminUser,)
    serializer_class = FlaggedLoanSerializer

    def get_queryset(self) -> List[LoanApplication]:
        """
        Return queryset of loans flagged for fraud.
        """
        return LoanApplication.objects.filter(status="FLAGGED").order_by("id")