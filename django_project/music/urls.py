from django.urls import path

from .views import *

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("browse", BrowseView.as_view(), name="browse"),
    path("browse/song/<int:pk>", SongView.as_view(), name="song"),
    path("new-playlist", NewPlaylistView.as_view(), name="new_playlist"),
    path("rename_playlist/<int:pk>", RenamePlaylistView.as_view(), name="rename_playlist"),
    path("detail_playlist/<int:pk>", DetailPlaylistView.as_view(), name="detail_playlist"),
    path("shared_playlist/<int:pk>", SharedPlaylistView.as_view(), name="shared_playlist"),
    path("save_playlist/<int:pk>", SavePlaylistView.as_view(), name="save_playlist"),
    path("remove_song/<int:pk>", RemoveSongView.as_view(), name="remove_song"),
    path("add_song/<int:p_pk>/<int:s_pk>", AddSongView.as_view(), name="add_song"),
    path("delete_playlist/<int:pk>", DeletePlaylistView.as_view(), name="delete_playlist"),
]