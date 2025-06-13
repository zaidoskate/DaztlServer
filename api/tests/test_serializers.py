import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import User, ArtistProfile, Song, Album, Playlist
from api.serializers import (
    UserSerializer, RegisterSerializer, ProfileUpdateSerializer,
    SongSerializer, AlbumSerializer, PlaylistSerializer,
    SongUploadSerializer, AlbumUploadSerializer, ArtistProfileSerializer
)

@pytest.mark.django_db
class TestUserSerializers:
    def test_user_serializer(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            role="listener"
        )
        
        serializer = UserSerializer(user)
        data = serializer.data
        
        assert data['username'] == "testuser"
        assert data['email'] == "test@example.com"
        assert data['first_name'] == "Test"
        assert data['last_name'] == "User"
        assert data['role'] == "listener"
        assert 'password' not in data  
    
    def test_register_serializer(self):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "first_name": "New",
            "last_name": "User",
            "role": "listener"
        }
        
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        
        user = serializer.save()
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.check_password("password123")  # Verifica que la contraseña se haya hasheado correctamente
        
    def test_profile_update_serializer(self):
        user = User.objects.create_user(
            username="updateuser",
            email="old@example.com",
            password="password123",
            first_name="Old",
            last_name="Name",
            role="listener"
        )
        
        update_data = {
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "Name"
        }
        
        serializer = ProfileUpdateSerializer(user, data=update_data)
        assert serializer.is_valid()
        
        updated_user = serializer.save()
        assert updated_user.email == "new@example.com"
        assert updated_user.first_name == "New"
        assert updated_user.last_name == "Name"
        assert updated_user.username == "updateuser"  # No debe cambiar

@pytest.mark.django_db
class TestContentSerializers:
    def setup_method(self):
        # Crear usuario artista
        self.user = User.objects.create_user(
            username="artist",
            email="artist@example.com",
            password="password123",
            role="artist"
        )
        
        # Crear perfil de artista
        self.artist_profile = ArtistProfile.objects.create(
            user=self.user,
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
    
    def test_song_serializer(self):
        serializer = SongSerializer(self.song)
        data = serializer.data
        
        assert data['title'] == "Test Song"
        assert data['artist_name'] == "artist"
        
    def test_artist_profile_serializer(self):
        serializer = ArtistProfileSerializer(self.artist_profile)
        data = serializer.data
        
        assert data['bio'] == "Test artist bio"
        assert data['user']['username'] == "artist"
        
    def test_song_upload_serializer(self):
        audio_file = SimpleUploadedFile(
            "new_song.mp3", 
            b"file_content", 
            content_type="audio/mpeg"
        )
        
        data = {
            "title": "Uploaded Song",
            "audio_file": audio_file
        }
        
        serializer = SongUploadSerializer(data=data)
        assert serializer.is_valid()