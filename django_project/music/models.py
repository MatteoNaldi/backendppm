from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Song(models.Model):
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    album = models.CharField(max_length=50)
    genre = models.CharField(max_length=20)
    year = models.IntegerField(default=None)
    duration = models.CharField(max_length=7)
    album_image = models.ImageField(upload_to='albums/')

    def __str__(self):
        return f"{self.title} - {self.author}"

class Playlist(models.Model):
    title = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.title} - {self.user}"

class SongInPlaylist(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.playlist.title} - {self.song.title}"