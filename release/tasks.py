from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_release_signature_confirmation(release_signature_id):
    from release.models import ReleaseSignature

    release_signature = ReleaseSignature.objects.get(id=release_signature_id)

    _subject = f"Signature confirmation: {release_signature.release.title}"
    _body_plaintext = f"""\
Hello {release_signature.nickname},

This is a confirmation that you signed the following release for
"{release_signature.release.title}":

{release_signature.release.release}

Legal Name: {release_signature.legal_name}
Date of Birth: {release_signature.dob}

Thanks!
- Philly Bike Action
    """
    _body_html = f"""
<p>Hello {release_signature.nickname},</p>
<p>
This is a confirmation that you signed the following release for
"{release_signature.release.title}":
</p>
<blockquote>
{release_signature.release.release}
</blockquote>
<p>
Legal Name: {release_signature.legal_name}<br>
Date of Birth: {release_signature.dob}
</p>
<p>
Thanks!<br>
- Philly Bike Action
</p>
    """

    send_mail(_subject, _body_plaintext, None, [release_signature.email], html_message=_body_html)
