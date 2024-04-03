from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from profiles.models import Profile, ShirtInterest


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["_user", "council_district"]
    search_fields = ["user__first_name", "user__last_name", "user__email"]
    autocomplete_fields = ("user",)

    def _user(self, obj=None):
        if obj is None:
            return ""
        return obj.user.email

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        else:
            return (
                "user",
                "mailchimp_contact_id",
            )


class ShirtInterestAdmin(admin.ModelAdmin):
    list_display = ["user", "fit", "size", "print_color"]
    list_filter = ["fit", "size", "print_color"]
    search_fields = ["user__first_name", "user__last_name", "user__email"]
    autocomplete_fields = ("user",)


admin.site.register(Profile, ProfileAdmin)


class UserAdmin(BaseUserAdmin):
    list_display = ["email", "first_name", "last_name", "is_staff", "is_superuser"]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(ShirtInterest, ShirtInterestAdmin)
