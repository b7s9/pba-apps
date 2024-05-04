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
    path("tshirt", views.ShirtInterestView.as_view(), name="shirt_interest"),
    path(
        "tshirt/<pk>/delete", views.ShirtInterestDeleteView.as_view(), name="shirt_interest_delete"
    ),
    path("tshirt/<shirt_id>/pay", views.create_tshirt_checkout_session, name="shirt_pay"),
    path(
        "tshirt/<shirt_id>/pay/complete",
        views.complete_tshirt_checkout_session,
        name="shirt_pay_complete",
    ),
]
