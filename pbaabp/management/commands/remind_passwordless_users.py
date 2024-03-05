import os
import urllib.parse
import sesame.utils
from django.urls import reverse

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Bother passwordless users to set a password"

    def handle(self, *args, **options):
        for user in User.objects.all():
            if not user.has_usable_password():
                    link = reverse("sesame_login")
                    link = f"https://apps.bikeaction.org{link}"
                    link += sesame.utils.get_query_string(user)
                    link += f"&next={reverse('account_set_password')}"
                    user.email_user(
                        subject=f"Welcome! Create a password for apps.bikeaction.org",
                        message=f"""\
Hello {user.first_name},

We created an account on apps.bikeaction.org so that you can manage your
new recurring donation to Philly Bike Action. Follow the link below to
set a password for your account.

    {link}

Thank you for being a part of the action!
""",
                    )
