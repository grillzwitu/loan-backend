"""
Module: Serializers for the loan app, handling serialization and
deserialization of LoanApplication objects.
"""

import logging
from typing import Any, Dict, Tuple, Type

from django.core.cache import cache
from rest_framework import serializers

from .models import LoanApplication

SERIALIZER_CACHE_TTL: int = 300  # Cache TTL for serializer outputs

logger: logging.Logger = logging.getLogger(__name__)


class LoanApplicationSerializer(serializers.ModelSerializer):
    """Serializer for LoanApplication instances to handle API input/output.

    Attributes:
        user (PrimaryKeyRelatedField): Read-only field representing
            the loan applicant.
    """

    user: serializers.PrimaryKeyRelatedField = (
        serializers.PrimaryKeyRelatedField(read_only=True)
    )

    class Meta:
        model: Type[LoanApplication] = LoanApplication
        fields: Tuple[str, ...] = (
            "id",
            "user",
            "amount",
            "purpose",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields: Tuple[str, ...] = (
            "id",
            "user",
            "status",
            "created_at",
            "updated_at",
        )

    def to_representation(self, instance: LoanApplication) -> Dict[str, Any]:
        """Cache serialized output for LoanApplication instances."""
        cache_key = f"serializer_loan_{instance.pk}"
        data = cache.get(cache_key)
        if data is not None:
            return data
        data = super().to_representation(instance)
        cache.set(cache_key, data, SERIALIZER_CACHE_TTL)
        return data

    def create(self, validated_data: Dict[str, Any]) -> LoanApplication:
        """Create and return a new LoanApplication instance for the given user.

        Args:
            validated_data (Dict[str, Any]): Validated data for the serializer.

        Returns:
            LoanApplication: The newly created loan application instance.
        """
        user = self.context["request"].user
        from .models import LoanApplication

        logger.info(
            "Serializer creating LoanApplication for user=%s with data=%s",
            user.username,
            validated_data,
        )
        return LoanApplication.objects.create(user=user, **validated_data)
