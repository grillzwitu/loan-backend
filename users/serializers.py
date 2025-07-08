"""
Module: Serializers for the users app, handling user data transformation
and registration.
"""

import logging
from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from rest_framework import serializers

logger: logging.Logger = logging.getLogger(__name__)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializes User instances for API responses (id, username, email).
    """

    class Meta:
        model = User
        fields = ("id", "username", "email")


class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles user registration, including write-only password field
    and user creation.
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data: Dict[str, Any]) -> AbstractUser:
        """
        Create a new User instance.

        Args:
            validated_data (Dict[str, Any]): Validated user creation data.

        Returns:
            User: The newly created User instance.
        """
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
        )
        logger.info("Registered new user: %s", user.username)
        return user
