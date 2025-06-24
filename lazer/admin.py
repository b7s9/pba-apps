from tempfile import TemporaryDirectory

from admin_extra_buttons.api import ExtraButtonsMixin, button
from asgiref.sync import async_to_sync
from django.contrib import admin

from lazer.integrations.submit_form import (
    MobilityAccessViolation,
    submit_form_with_playwright,
)
from lazer.models import ViolationReport, ViolationSubmission
from pbaabp.admin import ReadOnlyLeafletGeoAdminMixin


class ViolationSubmissionAdmin(ReadOnlyLeafletGeoAdminMixin, admin.ModelAdmin):
    list_display = (
        "image_tag_no_href",
        "captured_at",
        "created_by",
        "location",
    )
    readonly_fields = ("image_tag",)


class ViolationReportAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = (
        "image_tag_violation_no_href",
        "violation_observed_short",
        "created_by",
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

    @button(
        label="Resubmit",
        change_form=True,
        change_list=True,
        permission=lambda request, obj, **kw: bool(obj.screenshot_error),
    )
    def resubmit(self, request, object_id):
        report = ViolationReport.objects.get(pk=object_id)
        report.screenshot_error.delete()
        mobility_access_violation = MobilityAccessViolation(
            make=report.make,
            model=report.model,
            body_style=report.body_style,
            vehicle_color=report.vehicle_color,
            violation_observed=report.violation_observed,
            occurrence_frequency=report.occurrence_frequency,
            additional_information=report.additional_information,
            date_time_observed=None,
            _date_observed=report.date_observed,
            _time_observed=report.time_observed,
            address=None,
            _block_number=report.block_number,
            _street_name=report.street_name,
            _zip_code=report.zip_code,
        )
        with TemporaryDirectory() as temp_dir:
            violation = async_to_sync(submit_form_with_playwright)(
                submission=report.submission,
                violation=mobility_access_violation,
                photo=report.submission.image,
                screenshot_dir=temp_dir,
                violation_report=report,
            )
            violation.save()


admin.site.register(ViolationSubmission, ViolationSubmissionAdmin)
admin.site.register(ViolationReport, ViolationReportAdmin)
