from rest_framework import serializers
from .models import (
    User, ArtistProfile, Song, Album,
    Playlist, Notification, LiveChat, Like
)

# — CU-01 y CU-02: User & Profile
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','first_name','last_name','role']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username','email','password','first_name','last_name','role']
    def create(self, data):
        return User.objects.create_user(**data)

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','first_name','last_name']

# — CU-03: Buscar contenido
class SongSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source='artist.user.username', read_only=True)
    class Meta:
        model = Song
        fields = ['id','title','artist','artist_name','audio_file','release_date']

class AlbumSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source='artist.user.username', read_only=True)
    songs = SongSerializer(many=True, read_only=True)
    class Meta:
        model = Album
        fields = ['id','title','artist','artist_name','cover_image','songs']

class ArtistProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = ArtistProfile
        fields = ['id','user','bio','profile_picture']

# — CU-05/06/07: Playlists
class PlaylistSerializer(serializers.ModelSerializer):
    songs = serializers.PrimaryKeyRelatedField(many=True, queryset=Song.objects.all())
    class Meta:
        model = Playlist
        fields = ['id','name','songs','created_at']

# — CU-08/09: Subir contenido
class SongUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['title','audio_file']

class AlbumUploadSerializer(serializers.ModelSerializer):
    song_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    class Meta:
        model = Album
        fields = ['title','cover_image','song_ids']
    def create(self, data):
        songs = Song.objects.filter(id__in=data.pop('song_ids'))
        album = Album.objects.create(**data, artist=self.context['request'].user.artistprofile)
        album.songs.set(songs)
        return album

# — CU-10/11: Reportes
class ArtistReportSerializer(serializers.Serializer):
    total_songs = serializers.IntegerField()
    total_albums = serializers.IntegerField()
    total_likes = serializers.IntegerField()

class SystemReportSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_songs = serializers.IntegerField()
    total_albums = serializers.IntegerField()
    total_playlists = serializers.IntegerField()

# — CU-12: Chat en vivo
class LiveChatSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = LiveChat
        fields = ['id','song','user','message','timestamp']
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'artist', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
