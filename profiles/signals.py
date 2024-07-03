from allauth.socialaccount.models import SocialAccount
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from profiles.tasks import add_user_to_connected_role, remove_user_from_connected_role


@receiver(post_save, sender=SocialAccount, dispatch_uid="social_account_post_save")
def social_account_post_save(sender, instance, **kwargs):
    if instance.provider == "discord":
        add_user_to_connected_role.delay(instance.uid)


@receiver(post_delete, sender=SocialAccount, dispatch_uid="social_account_post_delete")
def social_account_post_delete(sender, instance, **kwargs):
    if instance.provider == "discord":
        remove_user_from_connected_role.delay(instance.uid)
