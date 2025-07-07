"""
Module: URL routing for user-related API endpoints
(registration, login, token refresh, and logout).

Defines URL patterns for user authentication workflows.
"""

from typing import Any, List

from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .views import LogoutView, RegisterView

urlpatterns: List[Any] = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
