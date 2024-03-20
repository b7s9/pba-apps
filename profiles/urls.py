from django.urls import path

from profiles import views

urlpatterns = [
    path("", views.ProfileDetailView.as_view(), name="profile"),
    path(
        "_partials/donations",
        views.ProfileDonationsPartial.as_view(),
        name="profile_donations_partial",
    ),
    path("edit", views.ProfileUpdateView.as_view(), name="profile_update"),
]
