from celery import shared_task

from lazer.models import ViolationReport
from lazer.utils import (
    submit_violation_report_to_ppa as _submit_violation_report_to_ppa,
)


@shared_task
def submit_violation_report_to_ppa(violation_id):
    violation_report = ViolationReport.objects.get(id=violation_id)
    _submit_violation_report_to_ppa(violation_report)
