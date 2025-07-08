import logging
from decimal import Decimal
from typing import Any, cast

from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from fraud.services import run_fraud_checks
from loan.models import LoanApplication
from loan.serializers import LoanApplicationSerializer

logger = logging.getLogger(__name__)
CACHE_TTL: int = 300  # Cache TTL in seconds for loan list endpoints


class LoanApplicationListCreateView(generics.ListCreateAPIView):
    """List and create LoanApplication instances for authenticated users."""

    permission_classes = (IsAuthenticated,)
    serializer_class = LoanApplicationSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Handle POST request to create a new LoanApplication for the
        authenticated user."""
        purpose = request.data.get("purpose", "")
        amount = request.data.get("amount")
        logger.info(
            "Creating LoanApplication for user=%s, amount=%s",
            request.user.username,
            amount,
        )
        loan = LoanApplication.objects.create(
            user_id=cast(int, request.user.pk),
            amount=Decimal(str(amount)),
            purpose=purpose,
        )
        run_fraud_checks(loan)
        loan.refresh_from_db()
        cache.delete("loan_list.all")
        cache.delete(f"loan_list.user_{request.user.pk}")
        cache.delete(f"serializer_loan_{loan.pk}")
        cache.delete(f"loan_detail_{loan.pk}")
        serializer = self.get_serializer(loan)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """List loan applications with caching for list endpoints."""
        key = (
            "loan_list.all"
            if request.user.is_staff
            else f"loan_list.user_{request.user.pk}"
        )
        data = cache.get(key)
        if data is not None:
            return Response(data)
        response = super().list(request, *args, **kwargs)
        cache.set(key, response.data, CACHE_TTL)
        return Response(response.data)

    def get_queryset(self):
        """Return the QuerySet of LoanApplication instances.

        Regular users: only their own loans.
        Admin users: all loans.
        """
        user = self.request.user
        if user.is_staff:
            return LoanApplication.objects.all().order_by("id")
        return (
            LoanApplication.objects.filter(
                user_id=cast(int, user.pk)
            )
            .order_by("id")
        )
