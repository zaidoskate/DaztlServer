import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import User, ArtistProfile, Song, Album, Playlist

@pytest.mark.django_db
class TestAuthViews:
    def setup_method(self):
        self.client = APIClient()
        self.register_url = reverse('register')  
        
    def test_register_view(self):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "first_name": "New",
            "last_name": "User",
            "role": "listener"
        }
        
        response = self.client.post(self.register_url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username="newuser").exists()
        
    def test_profile_update_view(self):
        # Crear usuario
        user = User.objects.create_user(
            username="updateuser",
            email="update@example.com",
            password="password123",
            first_name="Old",
            last_name="Name",
            role="listener"
        )
        
        # Autenticar usuario
        self.client.force_authenticate(user=user)
        
        # Actualizar perfil
        profile_url = reverse('profile-update')  
        data = {
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "Updated"
        }
        
        response = self.client.patch(profile_url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar que los datos se actualizaron
        user.refresh_from_db()
        assert user.email == "new@example.com"
        assert user.first_name == "New"
        assert user.last_name == "Updated"

@pytest.mark.django_db
class TestSongViews:
    def setup_method(self):
        self.client = APIClient()
        
        # Crear usuario artista
        self.artist_user = User.objects.create_user(
            username="testartist",
            email="artist@example.com",
            password="password123",
            role="artist"
        )
        
        # Crear perfil de artista
        self.artist_profile = ArtistProfile.objects.create(
            user=self.artist_user,
            bio="Test artist bio"
        )
        
        # Crear canción
        audio_file = SimpleUploadedFile(
            "song.mp3", 
            b"file_content", 
            content_type="audio/mpeg"
        )
        
        self.song = Song.objects.create(
            title="Test Song",
            artist=self.artist_profile,
            audio_file=audio_file
        )
        
    def test_song_list_view(self):
        url = reverse('song-list')  
        response = self.client.get(f"{url}?q=Test", format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['title'] == "Test Song"
        
    def test_song_detail_view(self):
        url = reverse('song-detail', kwargs={'pk': self.song.pk})  
        response = self.client.get(url, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "Test Song"
        assert response.data['artist_name'] == "testartist"
        
    def test_song_upload_view(self):
        # Autenticar como artista
        self.client.force_authenticate(user=self.artist_user)
        
        # Crear nueva canción
        url = reverse('song-upload')  
        audio_file = SimpleUploadedFile(
            "new_song.mp3", 
            b"file_content", 
            content_type="audio/mpeg"
        )
        
        data = {
            "title": "Uploaded Song",
            "audio_file": audio_file
        }
        
        response = self.client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verificar que la canción se creó
        assert Song.objects.filter(title="Uploaded Song").exists()

@pytest.mark.django_db
class TestPlaylistViews:
    def setup_method(self):
        self.client = APIClient()
        
        # Crear usuario
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            role="listener"
        )
        
        # Autenticar usuario
        self.client.force_authenticate(user=self.user)
        
        # Crear artista
        self.artist_user = User.objects.create_user(
            username="artist",
            email="artist@example.com",
            password="password123",
            role="artist"
        )
        
        self.artist_profile = ArtistProfile.objects.create(
            user=self.artist_user,
            bio="Test artist"
        )
        
        # Crear canción
        audio_file = SimpleUploadedFile(
            "song.mp3", 
            b"file_content", 
            content_type="audio/mpeg"
        )
        
        self.song = Song.objects.create(
            title="Playlist Song",
            artist=self.artist_profile,
            audio_file=audio_file
        )
        
    def test_playlist_create_view(self):
        url = reverse('playlist-create') 
        data = {
            "name": "My Playlist",
            "songs": [self.song.pk]
        }
        
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verificar que la playlist se creó
        assert Playlist.objects.filter(name="My Playlist").exists()
        
    def test_playlist_detail_view(self):
        # Crear playlist
        playlist = Playlist.objects.create(
            user=self.user,
            name="Test Playlist"
        )
        playlist.songs.add(self.song)
        
        url = reverse('playlist-detail', kwargs={'pk': playlist.pk}) 
        response = self.client.get(url, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "Test Playlist"
        assert self.song.pk in response.data['songs']