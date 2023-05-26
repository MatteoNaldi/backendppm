from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from .models import *


# Create your views here.

class DashboardView(LoginRequiredMixin, ListView):
    model = Playlist
    template_name = "dashboard.html"
    login_url = 'login'
    redirect_field_name = 'dashboard'

    def get_queryset(self):
        return Playlist.objects.all().filter(user=self.request.user)


class NewPlaylistView(LoginRequiredMixin, CreateView):
    model = Playlist
    template_name = "playlist/new_playlist.html"
    fields = ('title',)
    success_url = reverse_lazy("dashboard")
    login_url = 'login'
    redirect_field_name = 'dashboard'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PlaylistLoginRequired(LoginRequiredMixin):
    login_url = 'login'
    redirect_field_name = 'detail_playlist'


class RenamePlaylistView(PlaylistLoginRequired, UpdateView):
    model = Playlist
    template_name = "playlist/rename_playlist.html"
    fields = ('title',)

    def get_success_url(self):
        return reverse_lazy('detail_playlist', kwargs={'pk': self.kwargs["pk"]})


class DetailPlaylistView(PlaylistLoginRequired, DetailView):
    model = Playlist
    template_name = "playlist/detail_playlist.html"
    fields = ('title',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        song_list = SongInPlaylist.objects.all().filter(playlist=self.get_object().pk)
        all_songs = Song.objects.all()
        query = self.request.GET.get('search')
        if query:
            all_songs = all_songs.filter(title__icontains=query)
        author_filter = self.request.GET.get('author-filter')
        if author_filter:
            all_songs = all_songs.filter(author__icontains=author_filter)
        album_filter = self.request.GET.get('album-filter')
        if album_filter:
            all_songs = all_songs.filter(album__icontains=album_filter)
        genre_filter = self.request.GET.get('genre-filter')
        if genre_filter:
            all_songs = all_songs.filter(genre__icontains=genre_filter)
        if song_list:
            all_songs = all_songs.exclude(pk__in=song_list.values('song_id'))

        context['song_in_playlist'] = song_list
        context['all_songs'] = all_songs
        return context

class SharedPlaylistView(PlaylistLoginRequired, DetailView):
    model = Playlist
    template_name = "playlist/shared_playlist.html"
    fields = ('title',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        song_list = SongInPlaylist.objects.all().filter(playlist=self.get_object().pk)
        context['song_in_playlist'] = song_list
        return context

class SavePlaylistView(PlaylistLoginRequired, UpdateView):
    model = Playlist
    fields = '__all__'

    def post(self, request, *args, **kwargs):
        playlist = Playlist.objects.all().filter(pk=self.kwargs['pk']).get()
        my_playlist = Playlist(title = playlist.title, created=playlist.created, user=self.request.user)
        my_playlist.save()

        song_list=SongInPlaylist.objects.all().filter(playlist=playlist)
        for song in song_list:
            my_song_in_playlist = SongInPlaylist(playlist=my_playlist, song=song.song)
            my_song_in_playlist.save()
        return redirect('dashboard')

class AddSongView(PlaylistLoginRequired, UpdateView):
    model = Playlist
    fields = '__all__'

    def post(self, request, *args, **kwargs):
        playlist_pk = self.kwargs["p_pk"]
        song_pk = self.kwargs["s_pk"]
        playlist = Playlist.objects.all().filter(pk=playlist_pk).get()
        song = Song.objects.all().filter(pk=song_pk).get()
        song_in_playlist = SongInPlaylist(playlist = playlist, song=song)
        song_in_playlist.save()
        return redirect('detail_playlist', pk=playlist_pk)


class DeletePlaylistView(PlaylistLoginRequired, DeleteView):
    model = Playlist
    success_url = reverse_lazy('dashboard')


class RemoveSongView(PlaylistLoginRequired, DeleteView):
    model = SongInPlaylist
    playlist_pk = None

    def post(self, request, *args, **kwargs):
        self.playlist_pk = self.get_object().playlist.pk
        return super().post(args, kwargs)

    def get_success_url(self):
        return reverse_lazy('detail_playlist', kwargs={'pk': self.playlist_pk})


class BrowseView(LoginRequiredMixin, ListView):
    model = Song
    template_name = "browse.html"
    login_url = 'login'
    redirect_field_name = 'browse'


class SongView(LoginRequiredMixin, UpdateView):
    model = Song
    template_name = "song.html"
    fields = ('is_liked',)
    login_url = 'login'
    redirect_field_name = 'song'

    def get_success_url(self):
        return reverse_lazy('song', kwargs={'pk': self.kwargs["pk"]})

    def post(self, request, **kwargs):
        request.POST = request.POST.copy()
        request.POST['is_liked'] = not self.get_object().is_liked
        return super().post(request, **kwargs)
