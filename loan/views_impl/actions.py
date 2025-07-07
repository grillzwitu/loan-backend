import logging
from typing import Any

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from fraud.models import FraudFlag
from loan.models import LoanApplication
from loan.serializers import LoanApplicationSerializer

logger = logging.getLogger(__name__)


class LoanApplicationWithdrawView(APIView):
    """
    Allow users to withdraw a pending or flagged LoanApplication, changing its status to WITHDRAWN.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        loan = get_object_or_404(LoanApplication, pk=pk)
        if request.user != loan.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        logger.info(
            "User %s attempting to withdraw loan id=%s", request.user.username, pk
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
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        logger.info(
            "User %s successfully withdrew loan id=%s", request.user.username, pk
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoanApplicationApproveView(APIView):
    """
    Allow admin users to approve a pending or flagged LoanApplication.
    """

    permission_classes = (IsAdminUser,)

    def post(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        loan = get_object_or_404(LoanApplication, pk=pk)
        logger.info("Admin %s approving loan id=%s", request.user.username, pk)
        if loan.status not in ("PENDING", "FLAGGED"):
            return Response(
                {"detail": "Only pending or flagged loans can be approved"},
                status=status.HTTP_403_FORBIDDEN,
            )
        loan.status = "APPROVED"
        loan.save(update_fields=["status"])
        cache.delete(f"serializer_loan_{loan.pk}")
        serializer = LoanApplicationSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LoanApplicationRejectView(APIView):
    """
    Allow admin users to reject a pending or flagged LoanApplication.
    """

    permission_classes = (IsAdminUser,)

    def post(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        loan = get_object_or_404(LoanApplication, pk=pk)
        logger.info("Admin %s rejecting loan id=%s", request.user.username, pk)
        if loan.status not in ("PENDING", "FLAGGED"):
            return Response(
                {"detail": "Only pending or flagged loans can be rejected"},
                status=status.HTTP_403_FORBIDDEN,
            )
        loan.status = "REJECTED"
        loan.save(update_fields=["status"])
        cache.delete(f"serializer_loan_{loan.pk}")
        serializer = LoanApplicationSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LoanApplicationFlagView(APIView):
    """
    Allow admin users to manually flag a pending LoanApplication.
    """

    permission_classes = (IsAdminUser,)

    def post(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
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
                status=status.HTTP_403_FORBIDDEN,
            )
        FraudFlag.objects.create(loan=loan, reason=reason)
        loan.status = "FLAGGED"
        loan.save(update_fields=["status"])
        cache.delete(f"serializer_loan_{loan.pk}")
        serializer = LoanApplicationSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)
