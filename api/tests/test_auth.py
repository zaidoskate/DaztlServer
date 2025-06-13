import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User

@pytest.mark.django_db
class TestTokenAuth:
    def setup_method(self):
        self.client = APIClient()
        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username="authuser",
            email="auth@example.com",
            password="password123",
            role="listener"
        )
        
    def test_token_obtain(self):
        data = {
            "username": "authuser",
            "password": "password123"
        }
        
        response = self.client.post(self.login_url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        
        # Guardar token para prueba de refresco
        self.refresh_token = response.data['refresh']
        
    def test_token_refresh(self):
        # Primero obtener tokens
        data = {
            "username": "authuser",
            "password": "password123"
        }
        
        login_response = self.client.post(self.login_url, data, format='json')
        refresh_token = login_response.data['refresh']
        
        # Probar refresco del token
        refresh_data = {
            "refresh": refresh_token
        }
        
        response = self.client.post(self.refresh_url, refresh_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        
    def test_access_protected_endpoint_without_token(self):
        # Intentar acceder a un endpoint protegido sin token
        profile_url = reverse('profile-update')  
        response = self.client.get(profile_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    