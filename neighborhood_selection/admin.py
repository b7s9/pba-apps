from django.contrib import admin

from neighborhood_selection.models import Neighborhood


class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ["name", "approved"]
    list_filter = ["approved"]
    ordering = ["approved", "name"]

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return (
                "requests",
                "discord_role_id",
                "discord_channel_id",
            )
        else:
            return (
                "requests",
                "discord_role_id",
                "discord_channel_id",
            )


admin.site.register(Neighborhood, NeighborhoodAdmin)
