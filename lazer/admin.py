from admin_extra_buttons.api import ExtraButtonsMixin, button
from django.contrib import admin
from django.db.models import Q

from lazer.models import ViolationReport, ViolationSubmission
from lazer.tasks import submit_violation_report_to_ppa
from pbaabp.admin import ReadOnlyLeafletGeoAdminMixin


class ViolationSubmissionAdmin(ReadOnlyLeafletGeoAdminMixin, admin.ModelAdmin):
    list_display = (
        "image_tag_no_href",
        "captured_at",
        "created_by",
        "location",
    )
    readonly_fields = ("image_tag",)


class IsSubmittedFilter(admin.SimpleListFilter):
    title = "is submitted"
    parameter_name = "submitted"

    def lookups(self, request, model_admin):
        return ((True, "Yes"), (False, "No"))

    def queryset(self, request, queryset):
        if self.value() == "True":
            return queryset.filter(
                submitted__isnull=False,
            )
        elif self.value() == "False":
            return queryset.filter(Q(submitted__isnull=True))
        return queryset


class ViolationReportAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = (
        "image_tag_violation_no_href",
        "violation_observed_short",
        "is_submitted",
        "created_by",
        "date_observed",
        "time_observed",
    )
    list_filter = ("violation_observed", IsSubmittedFilter)
    list_select_related = True
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
        permission=lambda request, obj, **kw: bool(obj.screenshot_error) or obj.submitted is None,
    )
    def resubmit(self, request, object_id):
        report = ViolationReport.objects.get(pk=object_id)
        submit_violation_report_to_ppa.delay(report.id)


admin.site.register(ViolationSubmission, ViolationSubmissionAdmin)
admin.site.register(ViolationReport, ViolationReportAdmin)
