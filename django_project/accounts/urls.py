from django.urls import path, include

from .views import *


urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("", include("django.contrib.auth.urls")),
    path("user/<int:pk>", ProfileView.as_view(), name="profile"),
]
