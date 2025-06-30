import csv
import datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.safestring import mark_safe

from facets.models import District, RegisteredCommunityOrganization
from pbaabp.admin import ReadOnlyLeafletGeoAdminMixin
from profiles.models import DiscordActivity, Profile, ShirtOrder


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
            )
        elif self.value() == "False":
            return queryset.filter(Q(street_address__isnull=True) | Q(zip_code__isnull=True))
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


class DistrictFilter(admin.SimpleListFilter):
    title = "Council District (verified)"
    parameter_name = "council_district_verified"

    def lookups(self, request, model_amin):
        return [(f.id, f.name) for f in District.objects.all() if f.targetable]

    def queryset(self, request, queryset):
        if self.value():
            d = District.objects.get(id=self.value())
            return queryset.filter(location__within=d.mpoly)
        return queryset


class RCOFilter(admin.SimpleListFilter):
    title = "RCOs (verified)"
    parameter_name = "rcos_verified"

    def lookups(self, request, model_amin):
        return [
            (f.id, f.name) for f in RegisteredCommunityOrganization.objects.all() if f.targetable
        ]

    def queryset(self, request, queryset):
        if self.value():
            r = RegisteredCommunityOrganization.objects.get(id=self.value())
            return queryset.filter(location__within=r.mpoly)
        return queryset


class ProfileAdmin(ReadOnlyLeafletGeoAdminMixin, admin.ModelAdmin):
    list_display = [
        "_name",
        "_user",
        "discord_handle",
        "profile_complete",
        "apps_connected",
        "geolocated",
        "council_district_display",
        "council_district_validated",
    ]
    list_filter = [
        ProfileCompleteFilter,
        AppsConnectedFilter,
        GeolocatedFilter,
        DistrictFilter,
        RCOFilter,
        "council_district",
    ]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__socialaccount__extra_data__username",
    ]
    autocomplete_fields = ("user",)

    def _user(self, obj=None):
        if obj is None:
            return ""
        return obj.user.email

    def _name(self, obj=None):
        if obj is None:
            return ""
        return f"{obj.user.first_name} {obj.user.last_name}"

    def discord_handle(self, obj=None):
        if obj is None or obj.discord is None:
            return ""
        return obj.discord.extra_data["username"]

    def discord_activity(self, obj=None):
        if obj is None:
            return ""
        date_range_prev_60 = [
            timezone.now().date() - datetime.timedelta(days=(90 - i)) for i in range(60)
        ]
        date_range_last_30 = [
            timezone.now().date() - datetime.timedelta(days=(30 - i)) for i in range(31)
        ]
        query_prev_60 = DiscordActivity.objects.filter(
            profile=obj, date__in=date_range_prev_60
        ).all()
        query_last_30 = DiscordActivity.objects.filter(
            profile=obj, date__in=date_range_last_30
        ).all()
        counts_by_date_prev_60 = {activity.date: activity.count for activity in query_prev_60}
        counts_by_date_last_30 = {activity.date: activity.count for activity in query_last_30}
        counts_prev_60 = ",".join(
            [str(counts_by_date_prev_60.get(date, 0)) for date in date_range_prev_60]
        )
        counts_last_30 = ",".join(
            [str(counts_by_date_last_30.get(date, 0)) for date in date_range_last_30]
        )
        return mark_safe(
            f"""
            <div style="padding: 0; margin: 0; display: block; border-collapse: collapse;">
                <div
                    style="display: inline-block;"
                    data-sparkline="true"
                    data-points="{counts_prev_60}"
                    data-width="150"
                    data-height="50"
                    data-gap="0"
                ></div>
                <div
                    style="display: inline-block;"
                    data-colors="#83bd56"
                    data-sparkline="true"
                    data-points="{counts_last_30}"
                    data-width="75"
                    data-height="50"
                    data-gap="0"
                ></div>
            </div>
            """
        )

    discord_activity.help_text = "Discord activity over last 90 days, most recent 30 is in green"

    def geolocated(self, obj=None):
        if obj is None:
            return False
        return obj.location is not None

    geolocated.boolean = True

    def profile_complete(self, obj=None):
        if obj is None:
            return False
        return all(
            [
                obj.street_address is not None,
                obj.zip_code is not None,
            ]
        )

    profile_complete.boolean = True

    def apps_connected(self, obj=None):
        if obj is None:
            return False
        return obj.discord is not None

    apps_connected.boolean = True

    def council_district_calculated(self, obj=None):
        return obj.district

    council_district_calculated.short_description = "Calculated District"

    def council_district_validated(self, obj=None):
        if obj is None:
            return False
        if obj.council_district is None:
            return False
        if int(obj.council_district) == 0 and obj.district is None:
            return True
        if obj.location and obj.district is not None:
            if obj.council_district:
                return int(obj.district.name.split()[1]) == obj.council_district
            return False
        return False

    council_district_validated.boolean = True

    def council_district_display(self, obj=None):
        if obj is None:
            return None
        return obj.council_district

    council_district_display.short_description = "District"

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        else:
            return (
                "discord_activity",
                "user",
                "mailjet_contact_id",
                "council_district_calculated",
                "council_district_validated",
            )


@admin.action(description="Mark selected shirts as fulfilled")
def make_fulfilled(modeladmin, request, queryset):
    queryset.update(fulfilled=True)


@admin.action(description="Export Orders as CSV")
def csv_export(self, request, queryset):

    fields = [
        "shipping_method",
        "shipping_name",
        "shipping_line1",
        "shipping_line2",
        "shipping_city",
        "shipping_state",
        "shipping_postal_code",
        "get_fit_display",
        "get_print_color_display",
        "get_size_display",
    ]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=shirt-orders.csv"
    writer = csv.writer(response)
    writer.writerow(fields)
    for obj in queryset:
        writer.writerow(
            [
                obj.shipping_method,
                obj.shipping_name(),
                obj.shipping_line1(),
                obj.shipping_line2(),
                obj.shipping_city(),
                obj.shipping_state(),
                obj.shipping_postal_code(),
                obj.get_fit_display(),
                obj.get_print_color_display(),
                obj.get_size_display(),
            ]
        )

    return response


class ShirtOrderAdmin(ReadOnlyLeafletGeoAdminMixin, admin.ModelAdmin):
    list_display = ["user", "paid", "shipping_method", "fulfilled", "fit", "size", "print_color"]
    list_filter = ["paid", "shipping_method", "fulfilled", "fit", "size", "print_color"]
    search_fields = ["user__first_name", "user__last_name", "user__email"]
    autocomplete_fields = ("user",)
    readonly_fields = [
        "shipping_name",
        "shipping_line1",
        "shipping_line2",
        "shipping_city",
        "shipping_state",
        "shipping_postal_code",
    ]
    actions = [csv_export, make_fulfilled]


admin.site.register(Profile, ProfileAdmin)


class UserAdmin(BaseUserAdmin):
    list_display = ["email", "first_name", "last_name", "is_staff", "is_superuser"]
    fieldsets = (("Profile", {"fields": ("profile",)}),) + BaseUserAdmin.fieldsets
    add_fieldsets = (("Profile", {"fields": ("profile",)}),) + BaseUserAdmin.add_fieldsets
    readonly_fields = ["profile"]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(ShirtOrder, ShirtOrderAdmin)
