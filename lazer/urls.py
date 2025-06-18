from django.urls import path

from lazer import views

urlpatterns = [
    path("", views.submission, name="violation_submission"),
    path("list/", views.list, name="violation_list"),
    path("map/", views.map, name="violation_map"),
    path("submit/", views.submission_api, name="violation_submission_api"),
    path("report/", views.report_api, name="violation_report_api"),
    path("review/<str:submission_id>", views.review, name="violation_submission_review"),
]
