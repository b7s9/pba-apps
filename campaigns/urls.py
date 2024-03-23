from django.urls import path

from campaigns import views

urlpatterns = [
    path("", views.CampaignListView.as_view(), name="campaigns"),
    path("<slug:slug>", views.CampaignDetailView.as_view(), name="campaign"),
    path("petition/<slug:petition_slug_or_id>/sign", views.sign_petition, name="sign_petition"),
    path("<slug:slug>", views.CampaignDetailView.as_view(), name="campaign"),
]
