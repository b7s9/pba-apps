from django.contrib import admin

from lazer.models import ViolationSubmission
from pbaabp.admin import ReadOnlyLeafletGeoAdminMixin


class ViolationSubmissionAdmin(ReadOnlyLeafletGeoAdminMixin, admin.ModelAdmin):
    readonly_fields = ("image_tag",)


admin.site.register(ViolationSubmission, ViolationSubmissionAdmin)
