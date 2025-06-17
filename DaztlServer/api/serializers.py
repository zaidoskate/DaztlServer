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
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user
class ProfileUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# — CU-03: Buscar contenido
class SongSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source='artist.user.username', read_only=True)
    audio_url = serializers.ImageField(source='audio_file', read_only=True)
    cover_url = serializers.ImageField(source='cover_image', read_only=True)
    class Meta:
        model = Song
        fields = ['id','title','artist_name','audio_url','cover_url','release_date']


class AlbumSerializer(serializers.ModelSerializer):
    artist = serializers.PrimaryKeyRelatedField(read_only=True) 
    class Meta:
        model = Album
        fields = ['id','title','artist','cover_image']
        

class ArtistProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = ArtistProfile
        fields = ['id','user','bio','profile_picture']

# — CU-05/06/07: Playlists
class PlaylistSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)

    class Meta:
        model = Playlist
        fields = ['id','name','songs','created_at', 'cover']


# — CU-08/09: Subir contenido
class SongUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['title','audio_file', 'cover_image']

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
class ProfilePictureUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_picture']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'seen', 'created_at']