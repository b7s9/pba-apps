from django.contrib import admin

from lazer.models import ViolationReport, ViolationSubmission
from pbaabp.admin import ReadOnlyLeafletGeoAdminMixin


class ViolationSubmissionAdmin(ReadOnlyLeafletGeoAdminMixin, admin.ModelAdmin):
    list_display = (
        "image_tag_no_href",
        "captured_at",
        "location",
    )
    readonly_fields = ("image_tag",)


class ViolationReportAdmin(admin.ModelAdmin):
    list_display = (
        "image_tag_violation_no_href",
        "violation_observed_short",
        "date_observed",
        "time_observed",
    )
    list_filter = ("violation_observed",)
    readonly_fields = (
        "image_tag_violation",
        "image_tag_before_submit",
        "image_tag_after_submit",
        "image_tag_success",
        "image_tag_error",
        "image_tag_final",
    )


admin.site.register(ViolationSubmission, ViolationSubmissionAdmin)
admin.site.register(ViolationReport, ViolationReportAdmin)
