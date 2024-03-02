from django import forms
from django.utils.html import mark_safe

from profiles.models import Profile


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "email",
            "council_district",
            "zip_code",
            "newsletter_opt_in",
        ]

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

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(
        disabled=True,
        required=True,
        help_text=mark_safe('Update your email address <a href="/accounts/email/">here</a>'),
    )
