"""
Module: Serializers for the loan app, handling serialization and deserialization of LoanApplication objects.
"""
from rest_framework import serializers
from typing import Any, Dict, Tuple, Type
from .models import LoanApplication

class LoanApplicationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    """
    Serializer for LoanApplication instances to handle API input/output.
    """
    class Meta:
        model: Type[LoanApplication] = LoanApplication
        fields: Tuple[str, ...] = ("id", "user", "amount", "status", "created_at", "updated_at")
        read_only_fields: Tuple[str, ...] = ("id", "user", "status", "created_at", "updated_at")

    def create(self, validated_data: Dict[str, Any], user: Any) -> LoanApplication:
        """
        Create and return a new LoanApplication instance for the given user.

        Args:
            validated_data (Dict[str, Any]): Validated data for the serializer.
            user (Any): The authenticated user creating the loan application.

        Returns:
            LoanApplication: The newly created loan application instance.
        """
        from .models import LoanApplication
        return LoanApplication.objects.create(user=user, **validated_data)