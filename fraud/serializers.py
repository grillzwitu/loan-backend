"""
Module: Serializers for fraud app, handling FraudFlag and flagged loan views.
"""

import logging

from rest_framework import serializers

from loan.models import LoanApplication

from .models import FraudFlag

logger: logging.Logger = logging.getLogger(__name__)


class FraudFlagSerializer(serializers.ModelSerializer):
    """
    Serializer for FraudFlag instances to expose reason and timestamp.
    """

    class Meta:
        model = FraudFlag
        fields: tuple[str, ...] = ("id", "reason", "flagged_at")


class FlaggedLoanSerializer(serializers.ModelSerializer):
    """
    Serializer for LoanApplication instances including nested fraud flags.
    """

    fraud_flags = FraudFlagSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = LoanApplication
        fields: tuple[str, ...] = (
            "id",
            "user",
            "amount",
            "status",
            "created_at",
            "updated_at",
            "fraud_flags",
        )
        read_only_fields: tuple[str, ...] = (
            "id",
            "user",
            "amount",
            "status",
            "created_at",
            "updated_at",
            "fraud_flags",
        )
