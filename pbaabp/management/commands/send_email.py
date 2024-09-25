from django.core.management.base import BaseCommand

from pbaabp.email import send_email_message

TO = [
    "bikes@durbin.ee"
]

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("email_template", nargs="?", type=str)

    def handle(self, *args, **options):
        for email_address in TO:
            send_email_message(options["email_template"], None, [email_address], {})        
