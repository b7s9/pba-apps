from django.urls import path

from organizers import views

urlpatterns = [
    path("application/", views.organizer_application, name="organizer_application"),
    path("application/<pk>/edit/", views.organizer_application, name="organizer_application_edit"),
    path(
        "application/<pk>/view/",
        views.organizer_application_view,
        name="organizer_application_view",
    ),
]
