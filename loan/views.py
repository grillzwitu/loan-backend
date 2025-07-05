"""
Module: API views for the loan app, handling LoanApplication endpoints (list, create, retrieve, withdraw).
"""
import logging
from decimal import Decimal
from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import LoanApplication
from .serializers import LoanApplicationSerializer

logger: logging.Logger = logging.getLogger(__name__)

class LoanApplicationListCreateView(generics.ListCreateAPIView):
    """
    List and create LoanApplication instances for authenticated users.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = LoanApplicationSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Handle POST request to create a new LoanApplication for the authenticated user.
        """
        amount = request.data.get("amount")
        logger.info("Creating LoanApplication for user=%s, amount=%s", request.user.username, amount)
        loan = LoanApplication.objects.create(user=request.user, amount=Decimal(amount))
        serializer = self.get_serializer(loan)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self) -> QuerySet[LoanApplication]:
        """
        Return the QuerySet of LoanApplication instances for the requesting user.
        """
        return LoanApplication.objects.filter(user=self.request.user)

class LoanApplicationDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific LoanApplication by ID for authenticated users.
    """
    permission_classes = (IsAuthenticated,)
    queryset = LoanApplication.objects.all()
    serializer_class = LoanApplicationSerializer

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Handle GET request to retrieve a specific LoanApplication.
        """
        logger.info("Retrieving LoanApplication id=%s for user=%s", kwargs.get("pk"), request.user.username)
        return super().retrieve(request, *args, **kwargs)

class LoanApplicationWithdrawView(APIView):
    """
    Allow users to withdraw a pending LoanApplication,
    changing its status to WITHDRAWN.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        """
        Handle POST request to withdraw a pending loan.
        """
        loan = get_object_or_404(LoanApplication, pk=pk, user=request.user)
        logger.info("User %s attempting to withdraw loan id=%s", request.user.username, pk)
        try:
            loan.withdraw()
        except ValueError as e:
            logger.error(
                "Failed to withdraw loan id=%s for user=%s: %s", pk, request.user.username, str(e)
            )
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        logger.info("User %s successfully withdrew loan id=%s", request.user.username, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)