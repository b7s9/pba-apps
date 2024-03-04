from django.urls import path

from membership import views

urlpatterns = [
    path("add_card", views.create_setup_session, name="create_setup_session"),
    path(
        "checkout/one_time",
        views.create_one_time_donation_checkout_session,
        name="create_one_time_donation_checkout_session",
    ),
    path(
        "checkout/complete_one_time",
        views.complete_one_time_donation_checkout_session,
        name="complete_one_time_donation_checkout_session",
    ),
    path(
        "checkout/<str:price_id>",
        views.create_checkout_session,
        name="create_subscription_checkout_session",
    ),
    path(
        "complete_checkout_session",
        views.complete_checkout_session,
        name="complete_checkout_session",
    ),
    path("card/<str:payment_method_id>/remove", views.card_remove, name="remove_payment_method"),
    path(
        "card/<str:payment_method_id>/make_default",
        views.card_make_default,
        name="make_default_payment_method",
    ),
    path(
        "setup_recurring_donation", views.setup_recurring_donation, name="setup_recurring_donation"
    ),
    path(
        "cancel_recurring_donation/<str:subscription_id>",
        views.cancel_recurring_donation,
        name="cancel_recurring_donation",
    ),
    path(
        "change_recurring_donation/<str:subscription_id>",
        views.change_recurring_donation,
        name="change_recurring_donation",
    ),
]
