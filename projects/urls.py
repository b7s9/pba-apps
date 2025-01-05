from django.urls import path

from projects import views

urlpatterns = [
    path("application", views.project_application, name="project_application_form"),
]
