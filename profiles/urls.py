from django.urls import path

from profiles import views

urlpatterns = [
    path("", views.ProfileDetailView.as_view(), name="profile"),
    path("edit", views.ProfileUpdateView.as_view(), name="profile_update"),
]
