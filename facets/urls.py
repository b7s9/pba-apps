from django.urls import path

from facets import views

urlpatterns = [
    path("find", views.index),
    path("search", views.query_address, name="rco_search"),
]
