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
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'username', 'password']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        username = validated_data.get('username')
        if username and User.objects.filter(username=username).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({'username': 'Ya existe un usuario con este nombre.'})
        for attr, value in validated_data.items():
            if value:
                setattr(instance, attr, value)
        if password and password.strip():
            instance.set_password(password)
        instance.save()
        return instance

class ArtistProfileUpdateSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True, write_only=True)
    username = serializers.CharField(required=False, allow_blank=False)
    class Meta:
        model = User
        fields = ['username', 'password', 'bio']
    
    def update(self, instance, validated_data):
        bio = validated_data.pop('bio', None)
        
        for attr, value in validated_data.items():
            if attr == 'password' and value:
                if value and value.strip():
                    instance.set_password(value)
            elif attr != 'password':
                setattr(instance, attr, value)
        instance.save()
        
        if bio is not None and hasattr(instance, 'artistprofile'):
            instance.artistprofile.bio = bio
            instance.artistprofile.save()
        
        return instance


# — CU-03: Buscar contenido
class SongSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source='artist.user.username', read_only=True)
    audio_url = serializers.FileField(source='audio_file', read_only=True)
    cover_url = serializers.SerializerMethodField()
    
    def get_cover_url(self, obj):
        request = self.context.get('request')
        
        if obj.cover_image:
            if request:
                return request.build_absolute_uri(obj.cover_image.url) 
            return obj.cover_image.url  
        
        # Buscar en álbumes que contengan esta canción
        album_with_song = Album.objects.filter(songs=obj).first()
        if album_with_song and album_with_song.cover_image:
            if request:
                return request.build_absolute_uri(album_with_song.cover_image.url) 
            return album_with_song.cover_image.url  
            
        return None
    class Meta:
        model = Song
        fields = ['id','title','artist_name','audio_url','cover_url','release_date']


class AlbumSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)
    class Meta:
        model = Album
        fields = ['id','title','songs','cover_image']
        

class ArtistProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = ArtistProfile
        fields = ['id','user','bio']

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
        fields = ['title','audio_file', 'cover_image', 'release_date', 'artist_id']

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
        fields = ['id', 'user', 'message', 'is_broadcast', 'seen', 'created_at']

class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=500)
    
    def create(self, validated_data):
        return validated_data
