from django import forms


class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        help_text="The email address you used to sign up for your Philly Bike Action Account"
    )
