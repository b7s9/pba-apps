from django.contrib import admin

from events.models import EventSignIn, ScheduledEvent


class ScheduledEventAdmin(admin.ModelAdmin):
    list_display = ["title", "start_datetime", "status"]
    list_filter = ["status"]
    ordering = ["-status", "start_datetime"]


class EventSignInAdmin(admin.ModelAdmin):
    list_display = ["__str__", "council_district", "newsletter_opt_in"]


admin.site.register(ScheduledEvent, ScheduledEventAdmin)
admin.site.register(EventSignIn, EventSignInAdmin)
