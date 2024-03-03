from django.urls import path

from membership import views

urlpatterns = [
    path("add_card", views.create_checkout_session, name="create_checkout_session"),
    path(
        "checkout/<str:price_id>",
        views.create_checkout_session,
        name="create_subscription_checkout_session",
    ),
    path(
        "complete_card",
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
]
