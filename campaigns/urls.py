from django.urls import path

from campaigns import views

urlpatterns = [
    path("<slug:slug>", views.CampaignDetailView.as_view(), name="campaign"),
]
