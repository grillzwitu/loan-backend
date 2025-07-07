import logging
from typing import Any, cast

from django.core.cache import cache
from django.db.models.query import QuerySet
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from loan.models import LoanApplication
from loan.serializers import LoanApplicationSerializer

logger = logging.getLogger(__name__)
CACHE_TTL: int = 300  # Cache TTL in seconds for loan detail endpoints


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
        return LoanApplication.objects.filter(user_id=cast(int, user.pk))

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Handle GET request to retrieve a specific LoanApplication with caching.
        """
        pk = cast(int, kwargs.get("pk"))
        key = f"loan_detail_{pk}"
        data = cache.get(key)
        if data is not None:
            return Response(data)
        cache.delete(f"serializer_loan_{pk}")
        logger.info(
            "Retrieving LoanApplication id=%s for user=%s",
            pk,
            request.user.username,
        )
        response = super().retrieve(request, *args, **kwargs)
        fresh_loan = LoanApplication.objects.get(pk=pk)
        response.data["status"] = fresh_loan.status
        cache.set(key, response.data, CACHE_TTL)
        return response
