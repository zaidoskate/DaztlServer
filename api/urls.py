from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from . import views
    
urlpatterns = [
    # CU-01 / CU-02
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile-update'),
    path('login/', views.CustomLoginView.as_view(), name='login'),

    # CU-03 / CU-04
    path('songs/', views.SongListView.as_view(), name='song-list'),
    path('songs/<int:pk>/', views.SongDetailView.as_view(), name='song-detail'),
    path('albums/', views.AlbumListView.as_view()),
    path('artists/', views.ArtistListView.as_view()),

    # CU-05/06/07 Playlists
    path('playlists/', views.PlaylistCreateView.as_view(), name='playlist-create'),
    path('playlists/<int:pk>/', views.PlaylistDetailView.as_view(), name='playlist-detail'),

    # CU-08/09 Subir contenido
    path('songs/upload/', views.SongUploadView.as_view(), name='song-upload'),
    path('albums/upload/', views.AlbumUploadView.as_view()),

    # CU-10/11 Reportes
    path('reports/artist/', views.ArtistReportView.as_view()),
    path('reports/system/', views.SystemReportView.as_view()),

    # CU-12 Chat en vivo
    path('songs/<int:song_id>/chat/', views.LiveChatListView.as_view()),
    path('songs/<int:song_id>/chat/send/', views.LiveChatCreateView.as_view()),

    #CU-13 Like/unlike artista
    path('artists/<int:artist_id>/like/', views.like_artist, name='like-artist'), #POST
    path('artists/<int:artist_id>/like/status/', views.is_liked, name='is-liked'), #GET
]
