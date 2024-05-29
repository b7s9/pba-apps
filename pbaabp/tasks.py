from celery import shared_task
from django.conf import settings
from mailchimp3 import MailChimp, helpers


@shared_task
def subscribe_to_newsletter(email, tags=None):
    if tags is None:
        tags = []
    mailchimp = MailChimp(mc_api=settings.MAILCHIMP_API_KEY)
    mailchimp.lists.members.create_or_update(
        settings.MAILCHIMP_AUDIENCE_ID,
        helpers.get_subscriber_hash(email),
        {
            "email_address": email,
            "status_if_new": "subscribed",
        },
    )
    mailchimp.lists.members.tags.update(
        settings.MAILCHIMP_AUDIENCE_ID,
        helpers.get_subscriber_hash(email),
        data={"tags": [{"name": tag, "status": "active"} for tag in tags]},
    )
