from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser
from .models import (
    User, ArtistProfile, Song, Album,
    Playlist, Notification, Like, LiveChat
)
from .serializers import (
    RegisterSerializer, UserSerializer, ProfileUpdateSerializer,
    SongSerializer, AlbumSerializer, ArtistProfileSerializer,
    PlaylistSerializer, SongUploadSerializer, AlbumUploadSerializer,
    LiveChatSerializer, ArtistReportSerializer, SystemReportSerializer, LikeSerializer, ProfilePictureUploadSerializer
)

NotificationSerializer = None

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    

# Agrega esta nueva vista al final de tu views.py
class RegisterArtistView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        # Extraer datos del request
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        bio = request.data.get('bio', '')
        
        try:
            # Verificar si el usuario ya existe
            if User.objects.filter(username=username).exists():
                return Response({
                    'error': 'El nombre de usuario ya existe'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(email=email).exists():
                return Response({
                    'error': 'El email ya está registrado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear usuario con rol de artista
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='artist'  
            )
            
            # Crear perfil de artista
            artist_profile = ArtistProfile.objects.create(
                user=user,
                bio=bio
            )
            
            return Response({
                'message': 'Artista registrado exitosamente',
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'artist_profile_id': artist_profile.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)



class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user

class SongListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SongSerializer
    def get_queryset(self):
        q = self.request.query_params.get('q','')
        return Song.objects.filter(title__icontains=q)

class AlbumListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AlbumSerializer
    def get_queryset(self):
        q = self.request.query_params.get('q','')
        return Album.objects.filter(title__icontains=q)

class ArtistListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ArtistProfileSerializer
    def get_queryset(self):
        q = self.request.query_params.get('q','')
        return ArtistProfile.objects.filter(user__username__icontains=q)

class SongDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Song.objects.all()
    serializer_class = SongSerializer

class PlaylistCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlaylistSerializer
    def perform_create(self, ser): ser.save(user=self.request.user)

class PlaylistDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlaylistSerializer
    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user)

class AddSongToPlaylistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        song_id = request.data.get("song_id")
        try:
            playlist = Playlist.objects.get(pk=pk, user=request.user)
            song = Song.objects.get(pk=song_id)
            playlist.songs.add(song)
            return Response({"status": "success", "message": "Canción agregada correctamente"}, status=200)
        except Playlist.DoesNotExist:
            return Response({"status": "error", "message": "Playlist no encontrada"}, status=404)
        except Song.DoesNotExist:
            return Response({"status": "error", "message": "Canción no encontrada"}, status=404)

class PlaylistListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlaylistSerializer

    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user)

class SongUploadView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SongUploadSerializer
    def perform_create(self, ser):
        artist_profile = self.request.user.artistprofile
        ser.save(artist=artist_profile)

class AlbumUploadView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AlbumUploadSerializer
    def get_serializer_context(self):
        return {'request': self.request}

class ArtistReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, req):
        art = req.user.artistprofile
        data = {
            'total_songs': art.songs.count(),
            'total_albums': art.albums.count(),
            'total_likes': Like.objects.filter(artist=art).count()
        }
        return Response(ArtistReportSerializer(data).data)

class SystemReportView(APIView):
    permission_classes = [permissions.IsAdminUser]
    def get(self, _):
        data = {
            'total_users': User.objects.count(),
            'total_songs': Song.objects.count(),
            'total_albums': Album.objects.count(),
            'total_playlists': Playlist.objects.count()
        }
        return Response(SystemReportSerializer(data).data)

class LiveChatListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LiveChatSerializer
    def get_queryset(self):
        song_id = self.kwargs['song_id']
        return LiveChat.objects.filter(song_id=song_id)

class LiveChatCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LiveChatSerializer
    def perform_create(self, ser):
        ser.save(user=self.request.user)
        # CU-XX Obtener perfil del usuario autenticado
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        profile_picture_url = ""
        if user.profile_picture:
            profile_picture_url = request.build_absolute_uri(user.profile_picture.url)
        
        return Response({
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_image_url": profile_picture_url,
        })
class ProfilePictureUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = ProfilePictureUploadSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Like, ArtistProfile

# --- CU-13: Like/Unlike artista ---
@api_view(['POST'])
def like_artist(request, artist_id):
    try:
        artist = ArtistProfile.objects.get(id=artist_id)
    except ArtistProfile.DoesNotExist:
        return Response({"error": "Artista no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    Like.objects.get_or_create(user=request.user, artist=artist)
    return Response({"status": "Like agregado"}, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
def unlike_artist(request, artist_id):
    try:
        like = Like.objects.get(user=request.user, artist_id=artist_id)
    except Like.DoesNotExist:
        return Response({"error": "Like no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    like.delete()
    return Response({"status": "Like eliminado"}, status=status.HTTP_200_OK)

@api_view(['GET'])
def is_liked(request, artist_id):
    is_liked = Like.objects.filter(user=request.user, artist_id=artist_id).exists()
    return Response({"liked": is_liked}, status=status.HTTP_200_OK)

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomLoginView(TokenObtainPairView):
    class CustomTokenSerializer(TokenObtainPairSerializer):
        def validate(self, attrs):
            data = super().validate(attrs)
            user = self.user
            
            #Verificacion artista
            is_artist = user.role == 'artist'
            artist_profile_id = None
            if is_artist:
                try:
                    artist_profile_id = user.artisprofile.id
                except ArtistProfile.DoesNotExist:
                    artist_profile_id = None
            return {
                "token": data["access"],
                "refresh": data["refresh"],
                "user_info": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "is_artist": is_artist,
                    "artist_profile_id": artist_profile_id
                }
            }
    serializer_class = CustomTokenSerializer

