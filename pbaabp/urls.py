from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("accounts/profile/", include("profiles.urls")),
    path("events/", include("events.urls")),
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
    path("admin/", admin.site.urls),
]
