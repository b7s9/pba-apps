from django import forms
from django.utils.translation import gettext_lazy as _
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible


class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        help_text="The email address you used to sign up for your Philly Bike Action Account"
    )


class NewsletterSignupForm(forms.Form):
    footer_newsletter_signup_captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)

    footer_newsletter_signup_first_name = forms.CharField(
        required=True,
        label=_("First name"),
        widget=forms.TextInput(attrs={"hx-validate": "true", "placeholder": "First name"}),
    )
    footer_newsletter_signup_last_name = forms.CharField(
        label=_("Last name"),
        widget=forms.TextInput(attrs={"hx-validate": "true", "placeholder": "Last name"}),
        required=False,
    )
    footer_newsletter_signup_email = forms.EmailField(
        label=_("Email"),
        widget=forms.TextInput(
            attrs={"hx-validate": "true", "placeholder": "Email", "type": "email"}
        ),
    )
