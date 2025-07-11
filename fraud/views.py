"""
Module: API views for fraud app, handling flagged loan endpoints.
"""

import logging

from django.core.cache import cache
from django.db.models.query import QuerySet
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from loan.models import LoanApplication

from .serializers import FlaggedLoanSerializer

CACHE_TTL: int = 300  # Cache TTL in seconds for flagged list endpoints

logger: logging.Logger = logging.getLogger(__name__)


class FlaggedLoanListView(generics.ListAPIView):
    """List all flagged LoanApplication instances.

    Admin users only.
    """

    permission_classes = (IsAdminUser,)
    serializer_class = FlaggedLoanSerializer

    def list(self, request, *args, **kwargs) -> Response:
        """List flagged loans with caching for list endpoints."""
        page = request.query_params.get("page", 1)
        cache_key = f"flagged_loans_page_{page}"
        data = cache.get(cache_key)
        if data is not None:
            if isinstance(data, dict):
                return Response(data)
            return Response(
                {
                    "count": len(data),
                    "next": None,
                    "previous": None,
                    "results": data,
                }
            )
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response

    def get_queryset(self) -> QuerySet[LoanApplication]:
        """Return queryset of loans flagged for fraud."""
        return LoanApplication.objects.filter(status="FLAGGED").order_by("id")


class FlaggedLoanHistoryListView(generics.ListAPIView):
    """List all loans ever flagged (historical), regardless of current status.

    Admin users only.
    """

    permission_classes = (IsAdminUser,)
    serializer_class = FlaggedLoanSerializer

    def list(self, request, *args, **kwargs) -> Response:
        """List all historically flagged loans with caching."""
        page = request.query_params.get("page", 1)
        cache_key = f"flagged_loans_history_page_{page}"
        data = cache.get(cache_key)
        if data is not None:
            if isinstance(data, dict):
                return Response(data)
            return Response(
                {
                    "count": len(data),
                    "next": None,
                    "previous": None,
                    "results": data,
                }
            )
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response

    def get_queryset(self) -> QuerySet[LoanApplication]:
        """Return queryset of loans that have any fraud flag history."""
        return (
            LoanApplication.objects.filter(fraud_flags__isnull=False)
            .distinct()
            .order_by("id")
        )
