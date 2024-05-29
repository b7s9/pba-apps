from django.forms import ModelForm
from django.forms.widgets import DateInput

from release.models import ReleaseSignature


class ReleaseSignatureForm(ModelForm):
    class Meta:
        model = ReleaseSignature
        fields = [
            "legal_name",
            "nickname",
            "dob",
            "email",
        ]
        labels = {
            "dob": "Date of birth",
        }
        widgets = {"dob": DateInput(attrs={"type": "date"})}
        help_texts = {
            "legal_name": "Your legal name",
            "nickname": "How you would like us to address you, since legal names often differ",
            "dob": "Your date of birth",
            "email": "Your email, a copy of this release will be sent to you",
        }
