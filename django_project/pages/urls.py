from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from .views import *

urlpatterns = [
    path("", HomePageView.as_view(), name="homepage"),
]+ staticfiles_urlpatterns()
