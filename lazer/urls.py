from django.urls import path

from lazer import views

urlpatterns = [
    path("", views.submission, name="violation_submission"),
    path("review/<str:submission_id>", views.review, name="violation_submission_review"),
]
