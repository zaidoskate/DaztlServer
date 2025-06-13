import os
from django.utils.text import slugify
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('listener', 'Listener'),
        ('artist', 'Artist'),
        ('admin', 'DaztlAdmin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='listener')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.username
class ArtistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='artist_pics/', blank=True)

    def __str__(self):
        return f"ArtistProfile: {self.user.username}"

def clean_cover_filename(instance, filename):
    return f"song_covers/{filename}"
def clean_audio_filename(instance, filename):
    return f"songs/{filename}"
class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='songs')
    audio_file = models.FileField(upload_to=clean_audio_filename)
    cover_image = models.FileField(upload_to=clean_cover_filename)
    release_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title


class Album(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='albums')
    cover_image = models.ImageField(upload_to='album_covers/', blank=True)
    songs = models.ManyToManyField(Song)

    def __str__(self):
        return self.title


class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    name = models.CharField(max_length=255)
    songs = models.ManyToManyField(Song)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} liked {self.artist.user.username}"


class LiveChat(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.song.title}"
