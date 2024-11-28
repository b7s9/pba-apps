from celery import shared_task
from django.conf import settings
from mailchimp3 import MailChimp, helpers


@shared_task
def sync_to_mailchimp(event_signin_id):
    from events.models import EventSignIn

    event_sign_in = EventSignIn.objects.get(id=event_signin_id)

    if event_sign_in.newsletter_opt_in:
        mailchimp = MailChimp(mc_api=settings.MAILCHIMP_API_KEY)
        if event_sign_in.mailchimp_contact_id is None:
            print("creating contact...")
            response = mailchimp.lists.members.create_or_update(
                settings.MAILCHIMP_AUDIENCE_ID,
                helpers.get_subscriber_hash(event_sign_in.email),
                {
                    "email_address": event_sign_in.email,
                    "status_if_new": "subscribed",
                    "merge_fields": {
                        "FNAME": event_sign_in.first_name,
                        "LNAME": event_sign_in.last_name,
                    },
                },
            )
            event_sign_in.mailchimp_contact_id = response["id"]
            event_sign_in.save()

        print("updating tags...")
        mailchimp.lists.members.tags.update(
            settings.MAILCHIMP_AUDIENCE_ID,
            helpers.get_subscriber_hash(event_sign_in.email),
            data={
                "tags": [
                    {"name": "event-signin", "status": "active"},
                    {"name": f"district-{event_sign_in.council_district}", "status": "active"},
                    {
                        "name": (
                            f"attended-{event_sign_in.event.start_datetime.strftime('%Y-%m-%d')}-"
                            f"{event_sign_in.event.slug}"
                        ),
                        "status": "active",
                    },
                ]
            },
        )
