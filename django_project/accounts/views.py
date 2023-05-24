from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import RegisterForm


# Create your views here.

class SignUpView(CreateView):
    form_class = RegisterForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = "registration/profile.html"
    model = User
    success_url = reverse_lazy("dashboard")
    fields = ('username', 'email', )
    login_url = 'login'
    redirect_field_name = 'profile'