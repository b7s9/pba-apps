from django import forms


class SubmissionForm(forms.Form):

    latitude = forms.CharField()
    longitude = forms.CharField()
    image = forms.CharField()
