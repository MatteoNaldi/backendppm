from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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

    title = "My Favourite"

    def get(self, request, *args, **kwargs):
        Playlist.objects.get_or_create(title=self.title, user=request.user)
        return super().get(request, args, kwargs)

    def get_queryset(self):
        return Playlist.objects.all().filter(user=self.request.user).order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_liked_list = self.get_playlist(self.request.user)
        users = User.objects.all().exclude(id=self.request.user.id).order_by('pk')
        selected_user = self.get_closer_user(users, my_liked_list)
        recommended_list = self.get_playlist(selected_user).exclude(song_id__in=my_liked_list.values('song_id'))
        context['recommended_list'] = recommended_list
        return context

    def get_closer_user(self, users_list, my_liked_songs_list):
        fm = '0' + str(Song.objects.all().count()) + 'b'
        my_vec_bin = self.bin_vec(my_liked_songs_list, fm)
        mx = 0
        sel_user = None

        for user in users_list:
            user_liked_songs_list = self.get_playlist(user)
            vec_bin = self.bin_vec(user_liked_songs_list, fm)
            result = my_vec_bin and vec_bin
            count = str(result).count('1')
            if mx < count:
                mx = count
                sel_user = user
        return sel_user

    def bin_vec(self, vec, fm):
        string_vec = "".join(
            ["1" if song.id in list(vec.values_list('song', flat=True)) else "0" for song in Song.objects.all()])
        return format(int(string_vec, 2), fm)

    def get_playlist(self, user):
        return SongInPlaylist.objects.all().filter(playlist__user=user, playlist__title=self.title).order_by('pk')


class NewPlaylistView(LoginRequiredMixin, CreateView):
    model = Playlist
    template_name = "playlist/new_playlist.html"
    fields = ('title',)
    success_url = reverse_lazy("dashboard")
    login_url = 'login'
    redirect_field_name = 'dashboard'

    def form_valid(self, form):
        if form.instance.title == 'My Favourite':
            form.add_error("title", "Invalid Title")
            return super().form_invalid(form)
        form.instance.user = self.request.user
        return super().form_valid(form)


class LoginRequired(LoginRequiredMixin):
    login_url = 'login'
    redirect_field_name = 'detail_playlist'


class PlaylistPassesTest(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().title != "My Favourite"


class RenamePlaylistView(LoginRequired, PlaylistPassesTest, UpdateView):
    model = Playlist
    template_name = "playlist/rename_playlist.html"
    fields = ('title',)

    def get_success_url(self):
        return reverse_lazy('detail_playlist', kwargs={'pk': self.kwargs["pk"]})


class DetailPlaylistView(LoginRequired, ListView):
    model = Song
    template_name = "playlist/detail_playlist.html"

    def get_queryset(self):
        return Song.objects.all().filter(songinplaylist__in=self.get_songs())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_songs = Song.objects.all()
        all_songs = all_songs.exclude(songinplaylist__in=self.get_songs())
        context['all_songs'] = all_songs

        playlist = Playlist.objects.all().filter(pk=self.kwargs['pk']).get()
        context['playlist'] = playlist
        return context

    def post(self, request, *args, **kwargs):
        playlist = Playlist.objects.all().filter(pk=self.kwargs['pk']).get()
        song = Song.objects.all().filter(pk=request.POST.get('song_id')).get()
        song_in_playlist = SongInPlaylist(playlist=playlist, song=song)
        song_in_playlist.save()
        return redirect('detail_playlist', pk=self.kwargs['pk'])

    def get_songs(self):
        return SongInPlaylist.objects.all().filter(playlist__id=self.kwargs['pk'])


class SharedPlaylistView(LoginRequired, UserPassesTestMixin, ListView):
    model = Song
    template_name = "playlist/shared_playlist.html"

    def get_queryset(self):
        return Song.objects.all().filter(songinplaylist__in=self.get_songs())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        playlist = self.get_playlist()
        context['playlist'] = playlist
        return context

    def post(self, request, *args, **kwargs):
        playlist = self.get_playlist()

        my_playlist = Playlist(title=playlist.title, created=playlist.created, user=self.request.user)
        my_playlist.save()

        song_list = self.get_queryset()
        for song in song_list:
            my_song_in_playlist = SongInPlaylist(playlist=my_playlist, song=song)
            my_song_in_playlist.save()
        return redirect('dashboard')

    def test_func(self):
        return self.request.user != self.get_playlist().user

    def get_playlist(self):
        return Playlist.objects.all().filter(pk=self.kwargs['pk']).get()

    def get_songs(self):
        return SongInPlaylist.objects.all().filter(playlist__id=self.kwargs['pk'])


class DeletePlaylistView(LoginRequired, PlaylistPassesTest, DeleteView):
    model = Playlist
    success_url = reverse_lazy('dashboard')


class RemoveSongView(LoginRequired, DeleteView):
    model = Song

    def post(self, request, *args, **kwargs):
        song = SongInPlaylist.objects.all().filter(song__pk=self.kwargs['pk'])
        playlist_pk = song.get().playlist.pk
        song.delete()
        return redirect('detail_playlist', pk=playlist_pk)


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
