from django.contrib import admin

from organizers.models import OrganizerApplication


class OrganizerApplicationAdmin(admin.ModelAdmin):
    pass


admin.site.register(OrganizerApplication, OrganizerApplicationAdmin)
