from django.views.generic import DetailView

from campaigns.models import Campaign


class CampaignDetailView(DetailView):
    model = Campaign
