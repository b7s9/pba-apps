from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, UpdateView
from djstripe.models import Customer

from profiles.forms import ProfileUpdateForm
from profiles.models import Profile


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile

    def get_object(self, queryset=None):
        return self.request.user.profile


class ProfileDistrictAndRCOPartial(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "profiles/_rcos_partial.html"

    def get_object(self, queryset=None):
        return self.request.user.profile


class ProfileDonationsPartial(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "profiles/_donations_partial.html"

    def get_object(self, queryset=None):
        try:
            customer = Customer.objects.filter(subscriber=self.request.user).first()
            if customer:
                customer.api_retrieve()
                customer._sync_subscriptions()
                customer._sync_charges()
        except Exception:
            pass
        return self.request.user.profile


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm

    def get_success_url(self):
        return reverse("profile")

    def get_object(self):
        return Profile.objects.get(user=self.request.user)
