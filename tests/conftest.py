import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    """
    Returns an instance of the DRF APIClient for making HTTP requests in tests.
    """
    return APIClient()

@pytest.fixture
def user(db):
    """
    Create and return a default test user.
    """
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password"
    )
@pytest.fixture
def auth_client(api_client, user):
    """
    Returns an APIClient authenticated with a JWT access token for the test user.
    """
    login_data = {'username': user.username, 'password': 'password'}
    response = api_client.post('/api/users/login/', login_data, format='json')
    access_token = response.data.get('access')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    return api_client