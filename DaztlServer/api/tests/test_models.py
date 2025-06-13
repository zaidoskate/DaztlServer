import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import User, ArtistProfile, Song, Album, Playlist, LiveChat

@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            role="listener"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "listener"
        assert user.is_active
        assert not user.is_staff

    def test_create_artist_user(self):
        user = User.objects.create_user(
            username="artist1",
            email="artist@example.com",
            password="password123",
            role="artist"
        )
        
        # Crear perfil de artista
        artist_profile = ArtistProfile.objects.create(
            user=user,
            bio="This is a test artist bio"
        )
        
        assert user.role == "artist"
        assert artist_profile.bio == "This is a test artist bio"
        assert str(artist_profile) == f"ArtistProfile: {user.username}"

@pytest.mark.django_db
class TestSongModel:
    def test_create_song(self):
        # Crear usuario artista
        user = User.objects.create_user(
            username="artist2",
            email="artist2@example.com",
            password="password123",
            role="artist"
        )
        
        # Crear perfil de artista
        artist_profile = ArtistProfile.objects.create(
            user=user,
            bio="Artist for song test"
        )
        
        # Crear canción
        audio_file = SimpleUploadedFile(
            "test_song.mp3", 
            b"file_content", 
            content_type="audio/mpeg"
        )
        
        song = Song.objects.create(
            title="Test Song",
            artist=artist_profile,
            audio_file=audio_file
        )
        
        assert song.title == "Test Song"
        assert song.artist == artist_profile
        assert str(song) == "Test Song"

@pytest.mark.django_db
class TestAlbumModel:
    def test_create_album(self):
        # Crear usuario artista
        user = User.objects.create_user(
            username="artist3",
            email="artist3@example.com",
            password="password123",
            role="artist"
        )
        
        # Crear perfil de artista
        artist_profile = ArtistProfile.objects.create(
            user=user,
            bio="Artist for album test"
        )
        
        # Crear álbum
        album = Album.objects.create(
            title="Test Album",
            artist=artist_profile
        )
        
        assert album.title == "Test Album"
        assert album.artist == artist_profile
        assert str(album) == "Test Album"
        
@pytest.mark.django_db
class TestPlaylistModel:
    def test_create_playlist(self):
        # Crear usuario listener
        user = User.objects.create_user(
            username="listener1",
            email="listener@example.com",
            password="password123",
            role="listener"
        )
        
        # Crear playlist
        playlist = Playlist.objects.create(
            user=user,
            name="My Test Playlist"
        )
        
        assert playlist.name == "My Test Playlist"
        assert playlist.user == user
        assert str(playlist) == f"My Test Playlist - {user.username}"