from django.urls import path

from events import views

urlpatterns = [
    path("<slug:event_slug_or_id>", views.event_view),
    path("<slug:event_slug_or_id>/signin", views.event_signin, name="event_signin"),
    path(
        "<slug:event_slug_or_id>/kiosk-postroll",
        views.event_signin_kiosk_postroll,
        name="event_signin_kiosk_postroll",
    ),
]
