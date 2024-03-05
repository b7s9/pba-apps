from django.contrib import admin
from django.urls import include, path
from sesame.views import LoginView

from pbaabp.views import EmailLoginView

urlpatterns = [
    path("", include("pages.urls")),
    path("accounts/", include("allauth.urls")),
    path("accounts/profile/", include("profiles.urls")),
    path("events/", include("events.urls")),
    path("donations/", include("membership.urls")),
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
    path("sesame/login/", LoginView.as_view(), name="sesame_login"),
    path("email/login/", EmailLoginView.as_view(), name="email_login"),
    path("admin/", admin.site.urls),
]
