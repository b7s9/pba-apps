from django.conf import settings
from django.core.management.base import BaseCommand

from events.models import EventRSVP
from pbaabp.email import send_email_message


SENT = []


class Command(BaseCommand):

    def handle(*args, **kwargs):
        settings.EMAIL_SUBJECT_PREFIX = ""
        for rsvp in EventRSVP.objects.filter(event_id='e93a4037-dc63-4b11-850c-603928aabb80'):
            email = rsvp.email if rsvp.email else rsvp.user.email
            first_name = rsvp.first_name if rsvp.first_name else rsvp.user.first_name
            if email.lower() not in SENT:
                send_email_message(
                    "2nd-birthday-rsvp",
                    "Philly Bike Action <info@bikeaction.org>",
                    [email],
                    {"first_name": first_name},
                    reply_to=["info@bikeaction.org"],
                )
                SENT.append(email.lower())
            else:
                print(f"skipping {email}")

        print(len(SENT))
