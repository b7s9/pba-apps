import sesame.utils
from django.core.management.base import BaseCommand
from django.urls import reverse

from profiles.models import ShirtInterest


class Command(BaseCommand):
    help = "Remind users to pay for their shirts"

    def handle(self, *args, **options):
        for shirt in ShirtInterest.objects.filter(paid=False).all():
            link = reverse("sesame_login")
            link = f"https://apps.bikeaction.org{link}"
            link += sesame.utils.get_query_string(shirt.user)
            link += f"&next={reverse('shirt_pay', kwargs={'shirt_id': shirt.id})}"
            shirt.user.email_user(
                subject=(f"Hey {shirt.user.first_name}! Time to pay for your shirt!"),
                message=f"""\
Hello {shirt.user.first_name},

Great news! Our T-Shirt order is now in process!
The deposit is in, so it is time to pay for your shirt.

You can log into https://apps.bikeaction.org/accounts/profile/
and pay at the bottom of your profile,
or use the link below to go directly to the payment page.

    {link}

NOTE: This link will expire in 7 days!

Thank you for being a part of the action!
""",
                html_message=f"""
<p>Hello {shirt.user.first_name},</p>
<p>Great news! Our T-Shirt order is now in process!
The deposit is in, so it is time to pay for your shirt.</p>
<p>You can log into
<a href="https://apps.bikeaction.org/accounts/login/">apps.bikeaction.org</a>
and pay at the bottom of your profile,
or use the link below to go directly to the payment page.</p>
<p><a href="{link}">Pay Now</a></p>
<p><b>Note</b>:This link will expire in 7 days!</p>
<p>Thank you for being a part of the action!</p>
""",
            )
