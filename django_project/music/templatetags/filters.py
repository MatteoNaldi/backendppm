from django import template

register = template.Library()

@register.filter
def author_filter(value):
    author_list = [song.author for song in value]
    author_set = set(author_list)
    return author_set

@register.filter
def album_filter(value):
    album_list = [song.album for song in value]
    album_set = set(album_list)
    return album_set

@register.filter
def genre_filter(value):
    genre_list = [song.genre for song in value]
    genre_set = set(genre_list)
    return genre_set