from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.forms.widgets import OSMWidget
from django.db.models import Count, Q

from profiles.models import Profile, ShirtInterest


class ProfileCompleteFilter(admin.SimpleListFilter):
    title = "profile complete"
    parameter_name = "profile_complete"

    def lookups(self, request, model_admin):
        return ((True, "Yes"), (False, "No"))

    def queryset(self, request, queryset):
        if self.value() == "True":
            return queryset.filter(
                street_address__isnull=False,
                zip_code__isnull=False,
                council_district__isnull=False,
            )
        elif self.value() == "False":
            return queryset.filter(
                Q(street_address__isnull=True)
                | Q(zip_code__isnull=True)
                | Q(council_district__isnull=True)
            )
        return queryset


class GeolocatedFilter(admin.SimpleListFilter):
    title = "geolocated"
    parameter_name = "geolocated"

    def lookups(self, request, model_admin):
        return ((True, "Yes"), (False, "No"))

    def queryset(self, request, queryset):
        if self.value() == "True":
            return queryset.filter(
                location__isnull=False,
            )
        elif self.value() == "False":
            return queryset.filter(Q(location__isnull=True))
        return queryset


class AppsConnectedFilter(admin.SimpleListFilter):
    title = "apps connected"
    parameter_name = "apps_connected"

    def lookups(self, request, model_admin):
        return ((True, "Yes"), (False, "No"))

    def queryset(self, request, queryset):
        if self.value() == "True":
            return queryset.annotate(connected=Count("user__socialaccount")).filter(
                connected__gt=0
            )
        elif self.value() == "False":
            return queryset.annotate(connected=Count("user__socialaccount")).filter(connected=0)
        return queryset


class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "_name",
        "_user",
        "profile_complete",
        "apps_connected",
        "geolocated",
        "council_district",
    ]
    list_filter = [
        ProfileCompleteFilter,
        AppsConnectedFilter,
        GeolocatedFilter,
        "council_district",
    ]
    search_fields = ["user__first_name", "user__last_name", "user__email"]
    autocomplete_fields = ("user",)
    formfield_overrides = {
        models.PointField: {"widget": OSMWidget},
    }

    def _user(self, obj=None):
        if obj is None:
            return ""
        return obj.user.email

    def _name(self, obj=None):
        if obj is None:
            return ""
        return f"{obj.user.first_name} {obj.user.last_name}"

    def geolocated(self, obj=None):
        if obj is None:
            return False
        return not obj.location is None

    geolocated.boolean = True

    def profile_complete(self, obj=None):
        if obj is None:
            return False
        return all(
            [
                obj.street_address is not None,
                obj.zip_code is not None,
                obj.council_district is not None,
            ]
        )

    profile_complete.boolean = True

    def apps_connected(self, obj=None):
        if obj is None:
            return False
        return obj.discord is not None

    apps_connected.boolean = True

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        else:
            return (
                "user",
                "mailchimp_contact_id",
            )


@admin.action(description="Mark selected shirts as fulfilled")
def make_fulfilled(modeladmin, request, queryset):
    queryset.update(fulfilled=True)


class ShirtInterestAdmin(admin.ModelAdmin):
    list_display = ["user", "paid", "fulfilled", "fit", "size", "print_color"]
    list_filter = ["paid", "fulfilled", "fit", "size", "print_color"]
    search_fields = ["user__first_name", "user__last_name", "user__email"]
    autocomplete_fields = ("user",)
    actions = [make_fulfilled]


admin.site.register(Profile, ProfileAdmin)


class UserAdmin(BaseUserAdmin):
    list_display = ["email", "first_name", "last_name", "is_staff", "is_superuser"]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(ShirtInterest, ShirtInterestAdmin)
