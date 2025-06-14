from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
    
urlpatterns = [
    # CU-01 / CU-02
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/edit', views.ProfileUpdateView.as_view(), name='profile-update'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/upload_picture/', views.ProfilePictureUploadView.as_view()),
    path('login/', views.CustomLoginView.as_view(), name='login'),

    # CU-03 / CU-04
    path('songs/', views.SongListView.as_view()),
    path('songs/<int:pk>/', views.SongDetailView.as_view()),
    path('albums/', views.AlbumListView.as_view()),
    path('artists/', views.ArtistListView.as_view()),

    # CU-05/06/07 Playlists
    path('playlists/create/', views.PlaylistCreateView.as_view()),
    path('playlists/<int:pk>/', views.PlaylistDetailView.as_view()),
    path('playlists/<int:pk>/add_song/', views.AddSongToPlaylistView.as_view()),

    # CU-08/09 Subir contenido
    path('songs/upload/', views.SongUploadView.as_view()),
    path('albums/upload/', views.AlbumUploadView.as_view()),

    # CU-10/11 Reportes
    path('reports/artist/', views.ArtistReportView.as_view()),
    path('reports/system/', views.SystemReportView.as_view()),

    # CU-12 Chat en vivo
    path('songs/<int:song_id>/chat/', views.LiveChatListView.as_view()),
    path('songs/<int:song_id>/chat/send/', views.LiveChatCreateView.as_view()),

    #CU-13 Like/unlike artista
    path('artists/<int:artist_id>/like/', views.like_artist, name='like-artist'), #POST
    #Refresh del token necesario para mantener la sesión en los clientes (editar perfil en Android)
    path('artists/<int:artist_id>/like/status/', views.is_liked, name='is-liked'), #GET
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
