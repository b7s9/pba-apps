import time

from allauth.socialaccount.models import SocialAccount
from django.core.management.base import BaseCommand

from profiles.tasks import add_user_to_connected_role


class Command(BaseCommand):
    help = "Update roles for all connected discord auths"

    def handle(self, *args, **kwargs):
        for sa in SocialAccount.objects.filter(provider="discord"):
            add_user_to_connected_role.delay(sa.uid)
            time.sleep(10)
