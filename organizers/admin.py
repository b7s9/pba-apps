from django.contrib import admin

from organizers.models import OrganizerSubmission


class OrganizerSubmissionAdmin(admin.ModelAdmin):
    pass


admin.site.register(OrganizerSubmission, OrganizerSubmissionAdmin)
