from django.urls import path

from campaigns import views

urlpatterns = [
    path("", views.CampaignListView.as_view(), name="campaigns"),
    path("petition/<slug:petition_slug_or_id>/sign/", views.sign_petition, name="sign_petition"),
    path("petition/<slug:petition_slug_or_id>/heatmap/", views.heatmap, name="petition_heatmap"),
    path(
        "petition/<slug:petition_slug_or_id>/_signatures/",
        views.petition_signatures,
        name="petition_signatures",
    ),
    path("<slug:slug>/", views.CampaignDetailView.as_view(), name="campaign"),
]
