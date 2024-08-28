from allauth.account.forms import SignupForm as BaseSignupForm
from django import forms
from django.core.validators import RegexValidator
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _
from django_recaptcha.fields import ReCaptchaField

from profiles.models import Profile


class BaseProfileSignupForm(BaseSignupForm):
    first_name = forms.CharField(required=True, label=_("First Name"))
    last_name = forms.CharField(required=True, label=_("Last Name"))
    council_district = forms.ChoiceField(
        choices=Profile.District.choices, label=_("Council District")
    )
    street_address = forms.CharField(max_length=256, required=True, label=_("Street Address"))
    zip_code = forms.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^(^[0-9]{5}(?:-[0-9]{4})?$|^$)",
                message="Must be a valid zipcode in formats 19107 or 19107-3200",
            )
        ],
        label=_("Zip Code"),
    )
    newsletter_opt_in = forms.BooleanField(required=False, label=_("Newsletter Opt-In"))

    def save(self, request):
        user = super().save(request)
        user.username = user.email
        user.save()
        profile = Profile(
            user=user,
            council_district=self.cleaned_data["council_district"],
            zip_code=self.cleaned_data["zip_code"],
            newsletter_opt_in=self.cleaned_data["newsletter_opt_in"],
        )
        profile.save()
        return user


class ProfileSignupForm(BaseProfileSignupForm):
    captcha = ReCaptchaField()

    field_order = [
        "first_name",
        "last_name",
        "council_district",
        "street_address",
        "zip_code",
        "email",
        "newsletter_opt_in",
        "password1",
        "password2",
        "captcha",
    ]

    class Meta:
        help_texts = {
            "street_address": (
                "Your Philadelphia Street Address."
                "We use this to connect you with actions you can make "
                "in your neighborhood."
            ),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "email",
            "council_district",
            "street_address",
            "zip_code",
            "newsletter_opt_in",
        ]
        help_texts = {
            "street_address": (
                "Your Philadelphia Street Address."
                "We use this to connect you with actions you can make "
                "in your neighborhood."
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["first_name"].initial = kwargs["instance"].user.first_name
        self.fields["last_name"].initial = kwargs["instance"].user.last_name
        self.fields["email"].initial = kwargs["instance"].user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.first_name = self.cleaned_data["first_name"]
        profile.user.last_name = self.cleaned_data["last_name"]
        if commit:
            profile.save()
            profile.user.save()
        return profile

    first_name = forms.CharField(required=True, label=_("First Name"))
    last_name = forms.CharField(required=True, label=_("Last Name"))
    email = forms.EmailField(
        disabled=True,
        required=True,
        help_text=mark_safe('Update your email address <a href="/accounts/email/">here</a>'),
        label=_("Email"),
    )
