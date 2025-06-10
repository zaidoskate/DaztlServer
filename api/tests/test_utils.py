from rest_framework.test import APIClient
from api.models import User

def create_artist(username="artistuser", password="password123"):
    artist = User.objects.create_user(username=username, password=password, role="artist")
    client = APIClient()
    response = client.post('/api/login/', {"username": username, "password": password})
    token = response.data.get('token')
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return artist, client

def create_listener(username="listeneruser", password="password123"):
    listener = User.objects.create_user(username=username, password=password, role="listener")
    client = APIClient()
    response = client.post('/api/login/', {"username": username, "password": password})
    token = response.data.get('token')
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return listener, client
