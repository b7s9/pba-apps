from django.urls import path

from lazer import views

urlpatterns = [
    path("list/", views.list, name="violation_list"),
    path("map/", views.map, name="violation_map"),
    path("api/submit/", views.submission_api, name="violation_submission_api"),
    path("api/report/", views.report_api, name="violation_report_api"),
    path("api/login/", views.login_api, name="login_api"),
    path("api/logout/", views.logout_api, name="logout_api"),
    path("api/check-login/", views.check_login, name="check_login"),
]
