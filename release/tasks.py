from celery import shared_task

from pbaabp.email import send_email_message


@shared_task
def send_release_signature_confirmation(release_signature_id):
    from release.models import ReleaseSignature

    release_signature = ReleaseSignature.objects.get(id=release_signature_id)

    send_email_message(
        "release_signed", None, [release_signature.email], {"release_signature": release_signature}
    )
