from tempfile import TemporaryDirectory

from asgiref.sync import async_to_sync

from lazer.integrations.submit_form import (
    MobilityAccessViolation,
    submit_form_with_playwright,
)


def submit_violation_report_to_ppa(violation_report):
    violation_report.screenshot_error.delete()
    mobility_access_violation = MobilityAccessViolation(
        make=violation_report.make,
        model=violation_report.model,
        body_style=violation_report.body_style,
        vehicle_color=violation_report.vehicle_color,
        violation_observed=violation_report.violation_observed,
        occurrence_frequency=violation_report.occurrence_frequency,
        additional_information=violation_report.additional_information,
        date_time_observed=None,
        _date_observed=violation_report.date_observed,
        _time_observed=violation_report.time_observed,
        address=None,
        _block_number=violation_report.block_number,
        _street_name=violation_report.street_name,
        _zip_code=violation_report.zip_code,
    )
    with TemporaryDirectory() as temp_dir:
        violation = async_to_sync(submit_form_with_playwright)(
            submission=violation_report.submission,
            violation=mobility_access_violation,
            photo=violation_report.submission.image,
            screenshot_dir=temp_dir,
            violation_report=violation_report,
        )
        violation.save()
