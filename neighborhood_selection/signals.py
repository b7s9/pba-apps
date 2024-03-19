from django.db.models.signals import post_delete
from django.dispatch import receiver

from neighborhood_selection.models import Neighborhood
from neighborhood_selection.tasks import delete_neighborhood_role_and_channel


@receiver(post_delete, sender=Neighborhood, dispatch_uid="neighborhood_post_delete_signal")
def neighborhood_post_delete(sender, instance, using, origin, **kwargs):
    delete_neighborhood_role_and_channel.delay(
        instance.discord_role_id, instance.discord_channel_id
    )
