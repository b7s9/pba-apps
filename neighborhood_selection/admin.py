from django.contrib import admin

from neighborhood_selection.models import Neighborhood


class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ["name", "approved", "featured", "rcos_assigned"]
    list_filter = ["approved", "featured"]
    ordering = ["approved", "name"]
    autocomplete_fields = ["rcos"]

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return (
                "requests",
                "discord_role_id",
                "discord_channel_id",
                "rcos_assigned",
            )
        else:
            return (
                "requests",
                "discord_role_id",
                "discord_channel_id",
                "rcos_assigned",
            )

    def rcos_assigned(self, obj):
        return obj.rcos.count()


admin.site.register(Neighborhood, NeighborhoodAdmin)
