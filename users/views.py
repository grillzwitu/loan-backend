"""
Module: API views for user registration, login, token refresh, and logout.

This module provides endpoints for creating users, obtaining JWT tokens,
refreshing tokens, and logging out authenticated users.
"""

import logging
from typing import Any

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer

logger: logging.Logger = logging.getLogger(__name__)

# Removed jwt_payload_handler and jwt_encode_handler as simplejwt is now used


class RegisterView(generics.CreateAPIView):
    """
    Endpoint for creating a new user and returning a JWT token.
    """

    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Handle POST request for user registration and JWT issuance.

        Args:
            request (Request): The HTTP request containing user data.
            *args (Any): Additional positional arguments.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            Response: HTTP 201 Created with user data and JWT token.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        logger.info(
            "Issued JWT refresh and access tokens for user: %s",
            user.username,
        )
        data = {
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class LogoutView(APIView):
    """
    Endpoint for logging out authenticated users.
    Instructs client to discard the JWT.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:
        """
        Handle POST request to log out by instructing
        client to discard the JWT.

        Args:
            request (Request): The HTTP request for logout.

        Returns:
            Response: HTTP 204 No Content indicating successful logout.
        """
        # Client should discard token; no server-side action
        logger.info(
            "User %s logged out (logout endpoint called)",
            request.user.username,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
