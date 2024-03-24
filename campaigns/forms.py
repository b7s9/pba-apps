from django import forms

from campaigns.models import Petition, PetitionSignature


class PetitionSignatureForm(forms.ModelForm):
    class Meta:
        model = PetitionSignature
        fields = Petition.PetitionSignatureChoices.values

    send_email = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        petition = kwargs.pop("petition", None)
        requested_fields = kwargs.pop("requested_fields", [])
        required_fields = kwargs.pop("required_fields", [])
        super().__init__(*args, *kwargs)
        to_remove = []
        for field in self.fields.keys():
            if field not in requested_fields and field not in required_fields:
                to_remove.append(field)
        if petition.send_email:
            to_remove.remove("send_email")
        for field in to_remove:
            del self.fields[field]
        for field in self.fields.keys():
            if field in required_fields and field != "postal_address_line_2":
                self.fields[field].required = True
