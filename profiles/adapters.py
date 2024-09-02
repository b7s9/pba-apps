from allauth.account.adapter import DefaultAccountAdapter
from allauth.core import context  # noqa: F401
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.urls import reverse

from pbaabp.email import send_email_message


class AccountAdapter(DefaultAccountAdapter):
    def render_mail(self, template_prefix, email, context, headers=None):  # noqa: F811
        subject = render_to_string("{0}_subject.txt".format(template_prefix), context)
        subject = " ".join(subject.splitlines()).strip()
        subject = self.format_email_subject(subject)

        template_name = "{0}_message.txt".format(template_prefix)
        message = render_to_string(
            template_name,
            context,
            globals()["context"].request,
        ).strip()
        return subject, message

    def send_mail(self, template_prefix, email, context):  # noqa: F811
        ctx = {
            "email": email,
            "current_site": get_current_site(globals()["context"].request),
        }
        ctx.update(context)
        subject, message = self.render_mail(template_prefix, email, ctx)
        send_email_message(None, None, [email], None, subject=subject, message=message)


class SocialAccountAdapter(DefaultSocialAccountAdapter):

    def is_open_for_signup(self, request, socialaccount):
        return False

    def get_connect_redirect_url(self, request, socialaccount):
        return reverse("profile")
