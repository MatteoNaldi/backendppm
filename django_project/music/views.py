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

    def get(self, request, *args, **kwargs):
        Playlist.objects.get_or_create(title="My Favourite", user=request.user)
        return super().get(request, args, kwargs)

    def get_queryset(self):
        return Playlist.objects.all().filter(user=self.request.user).order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_liked_list = SongInPlaylist.objects.all().filter(playlist__user=self.request.user,
                                                            playlist__title='My Favourite').order_by('pk')
        users = User.objects.all().exclude(id=self.request.user.id).order_by('pk')
        selected_user = self.get_closer_user(users, my_liked_list)
        recommended_list = SongInPlaylist.objects.all().filter(playlist__user=selected_user,
                                                               playlist__title='My Favourite').exclude(
            song_id__in=my_liked_list.values('song_id'))
        context['recommended_list'] = recommended_list
        return context

    def get_closer_user(self, users_list, my_liked_songs_list):
        fm = '0' + str(Song.objects.all().count()) + 'b'
        my_vec_bin = format(int(self.gen_vec(my_liked_songs_list), 2), fm)
        mx = 0
        sel_user = None

        for user in users_list:
            user_liked_songs_list = SongInPlaylist.objects.all().filter(playlist__user=user,
                                                                        playlist__title='My Favourite').order_by('pk')
            vec_bin = format(int(self.gen_vec(user_liked_songs_list), 2), fm)
            result = my_vec_bin and vec_bin
            count = str(result).count('1')
            if mx < count:
                mx = count
                sel_user = user
        return sel_user

    def gen_vec(self, vec):
        all_song = Song.objects.all()
        my_vec = "".join(["1" if song.id in list(vec.values_list('song', flat=True)) else "0" for song in all_song])
        return my_vec


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


class DetailPlaylistView(PlaylistLoginRequired, UpdateView):
    model = Playlist
    template_name = "playlist/detail_playlist.html"
    fields = ('title',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        song_list = SongInPlaylist.objects.all().filter(playlist=self.get_object().pk)
        all_songs = Song.objects.all()
        if song_list:
            all_songs = all_songs.exclude(pk__in=song_list.values('song_id'))

        context['song_in_playlist'] = song_list
        context['all_songs'] = all_songs
        return context

    def post(self, request, *args, **kwargs):
        playlist = self.get_object()
        song = Song.objects.all().filter(pk=request.POST.get('song_id')).get()
        song_in_playlist = SongInPlaylist(playlist=playlist, song=song)
        song_in_playlist.save()
        return super().post(request, args, kwargs)


class SharedPlaylistView(PlaylistLoginRequired, UpdateView):
    model = Playlist
    template_name = "playlist/shared_playlist.html"
    fields = ('title',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        song_list = SongInPlaylist.objects.all().filter(playlist=self.get_object().pk)
        context['song_in_playlist'] = song_list
        return context

    def post(self, request, *args, **kwargs):
        playlist = self.get_object()
        my_playlist = Playlist(title=playlist.title, created=playlist.created, user=self.request.user)
        my_playlist.save()

        song_list = SongInPlaylist.objects.all().filter(playlist=playlist)
        for song in song_list:
            my_song_in_playlist = SongInPlaylist(playlist=my_playlist, song=song.song)
            my_song_in_playlist.save()
        return redirect('dashboard')


class DeletePlaylistView(PlaylistLoginRequired, DeleteView):
    model = Playlist
    success_url = reverse_lazy('dashboard')


class RemoveSongView(PlaylistLoginRequired, DeleteView):
    model = SongInPlaylist
    playlist_pk = None

    def post(self, request, *args, **kwargs):
        self.playlist_pk = self.get_object().playlist.pk
        return super().post(request, args, kwargs)

    def get_success_url(self):
        return reverse_lazy('detail_playlist', kwargs={'pk': self.playlist_pk})


class BrowseView(LoginRequiredMixin, ListView):
    model = Song
    template_name = "browse.html"
    login_url = 'login'
    redirect_field_name = 'browse'

    def get_queryset(self):
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

        return all_songs


class SongView(LoginRequiredMixin, DetailView):
    model = Song
    template_name = "song.html"
    login_url = 'login'
    redirect_field_name = 'song'
