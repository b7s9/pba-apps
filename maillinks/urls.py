from django.urls import path

from maillinks import views

urlpatterns = [
    path("send/<slug:slug>/", views.maillink, name="maillink_send"),
    path("view/<slug:slug>/", views.view, name="maillink_view"),
    path("flyer/<slug:slug>/", views.flyer, name="maillink_flyer"),
]
