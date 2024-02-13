from django.contrib import admin

from events.models import EventSignIn, ScheduledEvent


class ScheduledEventAdmin(admin.ModelAdmin):
    list_display = ["title", "start_datetime", "status"]
    list_filter = ["status"]
    ordering = ["-status", "start_datetime"]


class EventSignInAdmin(admin.ModelAdmin):
    list_display = ["get_name", "get_event", "council_district", "newsletter_opt_in"]
    list_filter = ["event__title"]
    ordering = ["-updated_at"]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_event(self, obj):
        return obj.event.title


admin.site.register(ScheduledEvent, ScheduledEventAdmin)
admin.site.register(EventSignIn, EventSignInAdmin)
