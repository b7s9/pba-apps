from django.contrib import admin

from lazer.models import ViolationSubmission

class ViolationSubmissionAdmin(admin.ModelAdmin):
    pass

admin.site.register(ViolationSubmission, ViolationSubmissionAdmin)
