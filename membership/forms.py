from django import forms

from membership.models import DonationTier


class RecurringDonationSetupForm(forms.Form):
    def _get_choices():
        return [(d.id, d.__str__()) for d in DonationTier.objects.filter(active=True).all()]

    donation_tier = forms.ChoiceField(choices=_get_choices)
