from django.urls import path

from facets import views

urlpatterns = [
    path("find/", views.index),
    path("search/", views.query_address, name="rco_search"),
    path("report/", views.report),
    path("rco/<str:rco_id>", views.rco, name="rco_detail"),
]
