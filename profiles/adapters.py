from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.urls import reverse


class SocialAccountAdapter(DefaultSocialAccountAdapter):

    def is_open_for_signup(self, request, socialaccount):
        return False

    def get_connect_redirect_url(self, request, socialaccount):
        return reverse("profile")
