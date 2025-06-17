from django.contrib import admin

from lazer.models import ViolationReport, ViolationSubmission
from pbaabp.admin import ReadOnlyLeafletGeoAdminMixin


class ViolationSubmissionAdmin(ReadOnlyLeafletGeoAdminMixin, admin.ModelAdmin):
    readonly_fields = ("image_tag",)


class ViolationReportAdmin(admin.ModelAdmin):
    readonly_fields = (
        "image_tag_before_submit",
        "image_tag_after_submit",
        "image_tag_success",
        "image_tag_error",
        "image_tag_final",
    )


admin.site.register(ViolationSubmission, ViolationSubmissionAdmin)
admin.site.register(ViolationReport, ViolationReportAdmin)
