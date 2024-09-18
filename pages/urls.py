from django.urls import path

from pages import views

urlpatterns = [
    path("", views.index, name="index"),
    path("donate", views.donate, name="donate"),
    path("brand", views.brand, name="brand"),
    path("policies/privacy-and-data", views.privacy, name="privacy"),
    path("policies/code-of-conduct", views.conduct, name="conduct"),
]
