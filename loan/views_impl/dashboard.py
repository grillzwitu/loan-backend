import logging
from typing import Any

from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from loan.models import LoanApplication

logger = logging.getLogger(__name__)
DASHBOARD_CACHE_TTL: int = 300  # Cache TTL in seconds for dashboard endpoint


class LoanDashboardView(APIView):
    """
    Dashboard endpoint returning counts of loans by status.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
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
