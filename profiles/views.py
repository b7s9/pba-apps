from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, UpdateView

from profiles.forms import ProfileUpdateForm
from profiles.models import Profile


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile

    def get_object(self, queryset=None):
        return self.request.user.profile


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm

    def get_success_url(self):
        return reverse("profile")

    def get_object(self):
        return Profile.objects.get(user=self.request.user)
