from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser
from rest_framework.parsers import FormParser
from django.db import IntegrityError
from .models import (
    User, ArtistProfile, Song, Album,
    Playlist, Notification, Like, LiveChat
)
from .serializers import (
    ChatMessageSerializer, RegisterSerializer, UserSerializer, ProfileUpdateSerializer, ArtistProfileUpdateSerializer,
    SongSerializer, AlbumSerializer, ArtistProfileSerializer,
    PlaylistSerializer, SongUploadSerializer,
    LiveChatSerializer, ArtistReportSerializer, SystemReportSerializer, LikeSerializer, ProfilePictureUploadSerializer, NotificationSerializer
)
from .consumers import connected_clients, connected_clients_chat


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    

class RegisterArtistView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        bio = request.data.get('bio', '')
        
        try:
            if User.objects.filter(username=username).exists():
                return Response({
                    'error': 'El nombre de usuario ya existe'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(email=email).exists():
                return Response({
                    'error': 'El email ya está registrado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='artist'  
            )
            
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

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError:
            return Response({'error: El nombre de usuario ya existe. Por favor elige otro'}, status=status.HTTP_400_BAD_REQUEST)

class ArtistProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ArtistProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        if request.user.role != 'artist':
            return Response({'error': 'Solo los artistas pueden usar este endpoint'}, status=status.HTTP_403_FORBIDDEN)
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError:
            return Response({'error: El nombre de usuario ya existe. Por favor elige otro'}, status=status.HTTP_400_BAD_REQUEST)


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

class PlaylistUploadCoverView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        try:
            playlist = Playlist.objects.get(pk=pk, user=request.user)
        except Playlist.DoesNotExist:
            return Response({"error": "Playlist no encontrada o no tienes permisos."}, status=status.HTTP_404_NOT_FOUND)

        file_obj = request.FILES.get('cover')

        if not file_obj:
            return Response({"error": "No se proporcionó ninguna imagen."}, status=status.HTTP_400_BAD_REQUEST)

        playlist.cover = file_obj
        playlist.save()

        return Response({"message": "Cover subido exitosamente."}, status=status.HTTP_200_OK)

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
    serializer_class = AlbumSerializer
    def perform_create(self, ser):
        artist_profile = self.request.user.artistprofile
        ser.save(artist=artist_profile)

class AddSongToAlbum(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        song_id = request.data.get("song_id")
        try:
            album = Album.objects.get(pk=pk, artist__user=request.user)
            song = Song.objects.get(pk=song_id)

            if album.songs.filter(pk=song_id).exists():
                return Response(
                    {"status": "info", "message": "La canción ya estaba en el álbum"},
                    status=status.HTTP_200_OK
                )

            album.songs.add(song)
            return Response({"status": "success", "message": "Canción agregada correctamente"}, status=200)
        except album.DoesNotExist:
            return Response({"status": "error", "message": "album no encontrada"}, status=404)
        except Song.DoesNotExist:
            return Response({"status": "error", "message": "Canción no encontrada"}, status=404)


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
        
class ArtistProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        if user.role != 'artist':
            return Response({
                'error': 'Solo los artistas pueden acceder a este endpoint'
            }, status=status.HTTP_403_FORBIDDEN)
            
        artist_profile = user.artistprofile
        profile_picture_url = ""
        if user.profile_picture:
            profile_picture_url = request.build_absolute_uri(user.profile_picture.url)
        
        return Response({
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_image_url": profile_picture_url,
            "bio": artist_profile.bio,
            "artist_profile_id": artist_profile.id
            
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

class ProfilePictureUploadGRPCView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        import base64
        from django.core.files.base import ContentFile
        
        user = request.user
        image_data = request.data.get('image_data')
        filename = request.data.get('filename', 'profile_image.jpg')
        
        image_content = base64.b64decode(image_data)
        image_file = ContentFile(image_content, name=filename)
        
        serializer = ProfilePictureUploadSerializer(user, data={'profile_picture': image_file}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Imagen actualizada',
                'image_url': request.build_absolute_uri(user.profile_picture.url)
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AdminReportsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, report_type):
        if request.user.role != 'admin':
            return Response({
                'error': 'Solo los administradores pueden acceder a los reportes'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            if report_type == 'users':
                return self.get_users_report()
            elif report_type == 'artists':
                return self.get_artists_report()
            elif report_type == 'listeners':
                return self.get_listeners_report()
            elif report_type == 'songs':
                return self.get_songs_report()
            elif report_type == 'albums':
                return self.get_albums_report()
            else:
                return Response({
                    'error': 'Tipo de reporte no válido'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_users_report(self):
        users = User.objects.all().values(
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'date_joined', 
        )
        return Response({
            'report_type': 'users',
            'total_count': users.count(),
            'data': list(users)
        })
    
    def get_artists_report(self):
        artists = User.objects.filter(role='artist').values(
            'id', 'username', 'email', 
            'first_name', 'last_name', 'date_joined', 
        )
        return Response({
            'report_type': 'artists',
            'total_count': artists.count(),
            'data': list(artists)
        })
    
    def get_listeners_report(self):
        listeners = User.objects.filter(role='listener').values(
            'id', 'username', 'email', 
            'first_name', 'last_name', 'date_joined',
        )
        return Response({
            'report_type': 'listeners',
            'total_count': listeners.count(),
            'data': list(listeners)
        })
    
    def get_songs_report(self):
        songs = Song.objects.all().values('id', 'title', 'release_date')
        return Response({
            'report_type': 'songs',
            'total_count': songs.count(),
            'data': list(songs)
        })
    
    def get_albums_report(self):
        albums = Album.objects.all().values('id', 'title')
        return Response({
            'report_type': 'albums',
            'total_count': albums.count(),
            'data': list(albums)
        })
        
class ArtistReportsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, report_type):
        user = request.user
        
        if user.role != 'artist':
            return Response({
                'error': 'Solo los artistas pueden acceder a estos reportes'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not hasattr(user, 'artistprofile'):
            return Response({
                'error': 'Perfil de artista no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            artist_profile = user.artistprofile
            
            if report_type == 'songs':
                return self.get_artist_songs_report(artist_profile)
            elif report_type == 'albums':
                return self.get_artist_albums_report(artist_profile)
            else:
                return Response({
                    'error': 'Tipo de reporte no válido'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_artist_songs_report(self, artist_profile):
        songs = Song.objects.filter(artist=artist_profile).values(
            'id', 'title', 'release_date'
        )
        
        return Response({
            'report_type': 'artist_songs',
            'total_count': songs.count(),
            'data': list(songs)
        })
    
    def get_artist_albums_report(self, artist_profile):
        albums = Album.objects.filter(artist=artist_profile).values(
            'id', 'title'
        )
        
        return Response({
            'report_type': 'artist_albums',
            'total_count': albums.count(),
            'data': list(albums)
        })


from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Like, ArtistProfile

# --- CU-13: Like/Unlike artista ---
@api_view(['POST', 'DELETE'])
def like_artist(request, artist_id):
    try:
        artist = ArtistProfile.objects.get(id=artist_id)
    except ArtistProfile.DoesNotExist:
        return Response({"error": "Artista no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        Like.objects.get_or_create(user=request.user, artist=artist)
        return Response({"status": "Like agregado"}, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        try:
            like = Like.objects.get(user=request.user, artist=artist)
            like.delete()
            return Response({"status": "Like eliminado"}, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            return Response({"error": "Like no encontrado"}, status=status.HTTP_404_NOT_FOUND)

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
                    artist_profile_id = user.artistprofile.id
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

class GlobalSearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')

        songs = Song.objects.filter(title__icontains=query)
        albums = Album.objects.filter(title__icontains=query)
        artists = ArtistProfile.objects.filter(user__username__icontains=query)
        playlists = Playlist.objects.filter(name__icontains=query)

        songs_data = SongSerializer(songs, many=True).data
        albums_data = AlbumSerializer(albums, many=True).data
        artists_data = ArtistProfileSerializer(artists, many=True).data
        playlists_data = PlaylistSerializer(playlists, many=True).data

        return Response({
            'songs': songs_data,
            'albums': albums_data,
            'artists': artists_data,
            'playlists': playlists_data
        })
    
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Solo mostrar notificaciones del usuario actual
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

class NotificationCreateView(generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        notification = serializer.save(user=self.request.user)
        payload = {
            "id" : notification.id,
            "type": "notification",
            "message": notification.message,
            "created_at": notification.created_at.isoformat() 
        }
        if notification.is_broadcast:
            for client in list(connected_clients):
                async_to_sync(client.send_personal)(payload)

class ChatSendView(generics.CreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        message_data = serializer.validated_data
        
        payload = {
            "type": "chat_message",
            "username": self.request.user.username,
            "message": message_data['message']
        }
        
        for client in list(connected_clients_chat):
            async_to_sync(client.send_personal)(payload)
        
        return None
    
class NotificationMarkAsSeenView(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']  # Solo permitir PATCH

    def get_queryset(self):
        # Solo permitir actualizar notificaciones del usuario actual
        return Notification.objects.filter(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.seen = True
        instance.save()
        return Response(self.get_serializer(instance).data)

class UnseenNotificationCountView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        count = Notification.objects.filter(user=request.user, seen=False).count()
        return Response({'unseen_count': count})