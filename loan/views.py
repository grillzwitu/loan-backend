"""
Module: API views for the loan app, handling
LoanApplication endpoints for list, create,
retrieve, withdraw, approve, reject, and flag.
"""

import logging
from decimal import Decimal
from typing import Any, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser as User
else:
    from django.contrib.auth import get_user_model
    User = get_user_model()

from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.core.cache import cache

from rest_framework import generics, status
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from fraud.models import FraudFlag
from fraud.services import run_fraud_checks

from .models import LoanApplication
from .serializers import LoanApplicationSerializer


logger: logging.Logger = logging.getLogger(__name__)


CACHE_TTL: int = 300  # Cache TTL in seconds for loan list endpoints


class LoanApplicationListCreateView(generics.ListCreateAPIView):
    """
    List and create LoanApplication instances for authenticated users.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = LoanApplicationSerializer

    def create(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """
        Handle POST request to create a new
        LoanApplication for the authenticated user.
        """
        amount = request.data.get("amount")
        logger.info(
            "Creating LoanApplication for user=%s, amount=%s",
            request.user.username,
            amount,
        )
        loan = LoanApplication.objects.create(
            user_id=cast(int, request.user.pk),
            amount=Decimal(str(amount)),
        )
        # Run fraud checks (in case signal is disconnected)
        # and refresh instance to include status changes
        run_fraud_checks(loan)
        loan.refresh_from_db()
        cache.delete("loan_list.all")
        cache.delete(f"loan_list.user_{request.user.pk}")
        cache.delete(f"serializer_loan_{loan.pk}")
        cache.delete(f"loan_detail_{loan.pk}")
        serializer = self.get_serializer(loan)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def list(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """
        List loan applications with caching for list endpoints.
        """
        if request.user.is_staff:
            key = "loan_list.all"
        else:
            key = f"loan_list.user_{request.user.pk}"
        data = cache.get(key)
        if data is not None:
            return Response(data)
        response = super().list(request, *args, **kwargs)
        cache.set(key, response.data, CACHE_TTL)
        return response

    def get_queryset(self) -> QuerySet[LoanApplication]:
        """
        Return the QuerySet of LoanApplication instances.
        Regular users: only their own loans.
        Admin users: all loans.
        """
        user = self.request.user
        if user.is_staff:
            return LoanApplication.objects.all().order_by("id")
        user_obj = cast(User, self.request.user)
        return LoanApplication.objects.filter(
            user_id=user_obj.pk,
        ).order_by("id")


class LoanApplicationDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific LoanApplication by ID for authenticated users.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = LoanApplicationSerializer

    def get_queryset(self) -> QuerySet[LoanApplication]:
        """
        Restrict loans so regular users can only view their own
        loans, while admin users can view all loans.
        """
        user = self.request.user
        if user.is_staff:
            return LoanApplication.objects.all()
        user_obj = cast(User, self.request.user)
        return LoanApplication.objects.filter(
            user_id=user_obj.pk,
        )

    def retrieve(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """
        Handle GET request to retrieve a specific LoanApplication with caching.
        """
        # Caching detail response
        pk = cast(int, kwargs.get("pk"))
        key = f"loan_detail_{pk}"
        data = cache.get(key)
        if data is not None:
            return Response(data)
        # Clear serializer cache to ensure fresh representation
        cache.delete(f"serializer_loan_{pk}")
        logger.info(
            "Retrieving LoanApplication id=%s for user=%s",
            pk,
            request.user.username,
        )
        response = super().retrieve(request, *args, **kwargs)
        # Override status to ensure fresh DB value after cache miss
        fresh_loan = LoanApplication.objects.get(pk=pk)
        response.data["status"] = fresh_loan.status
        cache.set(key, response.data, CACHE_TTL)
        return response


class LoanApplicationWithdrawView(APIView):
    """
    Allow users to withdraw a pending
    LoanApplication, changing its status to WITHDRAWN.
    """

    permission_classes = (IsAuthenticated,)

    def post(
        self,
        request: Request,
        pk: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """
        Handle POST request to withdraw a pending loan.
        """
        loan = get_object_or_404(LoanApplication, pk=pk, user=request.user)
        logger.info(
            "User %s attempting to withdraw loan id=%s",
            request.user.username,
            pk,
        )
        try:
            loan.withdraw()
        except ValueError as e:
            logger.error(
                "Failed to withdraw loan id=%s for user=%s: %s",
                pk,
                request.user.username,
                str(e),
            )
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        logger.info(
            "User %s successfully withdrew loan id=%s",
            request.user.username,
            pk,
        )
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


# Admin endpoints for loan approval, rejection, and manual flagging


class LoanApplicationApproveView(APIView):
    """
    Allow admin users to approve a pending
    or flagged LoanApplication.
    """

    permission_classes = (IsAdminUser,)

    def post(
        self,
        request: Request,
        pk: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        loan = get_object_or_404(LoanApplication, pk=pk)
        logger.info(
            "Admin %s approving loan id=%s",
            request.user.username,
            pk,
        )
        if loan.status not in ("PENDING", "FLAGGED"):
            return Response(
                {"detail": "Only pending or flagged loans can be approved"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        loan.status = "APPROVED"
        loan.save(update_fields=["status"])
        cache.delete(f"serializer_loan_{loan.pk}")
        serializer = LoanApplicationSerializer(loan)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class LoanApplicationRejectView(APIView):
    """
    Allow admin users to reject a pending
    or flagged LoanApplication.
    """

    permission_classes = (IsAdminUser,)

    def post(
        self,
        request: Request,
        pk: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        loan = get_object_or_404(LoanApplication, pk=pk)
        logger.info(
            "Admin %s rejecting loan id=%s",
            request.user.username,
            pk,
        )
        if loan.status not in ("PENDING", "FLAGGED"):
            return Response(
                {"detail": "Only pending or flagged loans can be rejected"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        loan.status = "REJECTED"
        loan.save(update_fields=["status"])
        cache.delete(f"serializer_loan_{loan.pk}")
        serializer = LoanApplicationSerializer(loan)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class LoanApplicationFlagView(APIView):
    """
    Allow admin users to manually flag a pending
    LoanApplication.
    """

    permission_classes = (IsAdminUser,)

    def post(
        self,
        request: Request,
        pk: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        loan = get_object_or_404(LoanApplication, pk=pk)
        reason = request.data.get("reason", "Manually flagged by admin")
        logger.info(
            "Admin %s manually flagging loan id=%s for reason: %s",
            request.user.username,
            pk,
            reason,
        )
        if loan.status != "PENDING":
            return Response(
                {"detail": "Only pending loans can be flagged"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        FraudFlag.objects.create(loan=loan, reason=reason)
        loan.status = "FLAGGED"
        loan.save(update_fields=["status"])
        cache.delete(f"serializer_loan_{loan.pk}")
        serializer = LoanApplicationSerializer(loan)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# Dashboard endpoint: counts by status with caching
DASHBOARD_CACHE_TTL: int = 300  # Cache TTL in seconds for dashboard endpoint


class LoanDashboardView(APIView):
    """
    Dashboard endpoint returning counts of loans by status.
    """
    permission_classes = (IsAuthenticated,)

    def get(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """
        Handle GET request for loan status dashboard counts.
        """
        cache_key = "loan_dashboard"
        data = cache.get(cache_key)
        if data is not None:
            return Response(data)
        # Build counts per status
        statuses = [choice[0] for choice in LoanApplication.STATUS_CHOICES]
        result: dict[str, int] = {}
        for status_name in statuses:
            count = LoanApplication.objects.filter(status=status_name).count()
            result[status_name] = count
        cache.set(cache_key, result, DASHBOARD_CACHE_TTL)
        return Response(result)
