from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from .models import (
    User, ArtistProfile, Song, Album,
    Playlist, Notification, Like, LiveChat
)
from .serializers import (
    RegisterSerializer, UserSerializer, ProfileUpdateSerializer,
    SongSerializer, AlbumSerializer, ArtistProfileSerializer,
    PlaylistSerializer, SongUploadSerializer, AlbumUploadSerializer,
    LiveChatSerializer, ArtistReportSerializer, SystemReportSerializer, LikeSerializer
)

NotificationSerializer = None

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

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
