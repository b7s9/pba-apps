from django import forms

from membership.models import DonationTier


class RecurringDonationSetupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        tier_id = kwargs.pop("tier_id", None)
        if tier_id is not None:
            kwargs.update(initial={"donation_tier": tier_id})

        super(RecurringDonationSetupForm, self).__init__(*args, **kwargs)

    def _get_choices():
        return [(d.id, d.__str__()) for d in DonationTier.objects.filter(active=True).all()]

    donation_tier = forms.ChoiceField(choices=_get_choices, widget=forms.RadioSelect())
