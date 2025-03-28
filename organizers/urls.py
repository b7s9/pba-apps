from django.urls import path

from organizers import views

urlpatterns = [
    path("form/", views.organizer_form, name="organizer_form"),
    path("form/<pk>/edit", views.organizer_form, name="organizer_form_edit"),
    path("form/<pk>/view", views.organizer_form_view, name="organizer_form_view"),
]
