import asyncio
import base64
import datetime
import json
import secrets

from anyio import TemporaryDirectory
from django.contrib.gis.geos import Point
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import aget_object_or_404, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt

from facets.utils import reverse_geocode_point
from lazer.forms import ReportForm, SubmissionForm
from lazer.integrations.platerecognizer import read_plate
from lazer.integrations.submit_form import (
    MobilityAccessViolation,
    submit_form_with_playwright,
)
from lazer.models import ViolationReport, ViolationSubmission


def get_image_from_data_url(data_url):
    _format, _dataurl = data_url.split(";base64,")
    _filename, _extension = secrets.token_hex(20), _format.split("/")[-1]

    file = ContentFile(base64.b64decode(_dataurl), name=f"{_filename}.{_extension}")

    return file, (_filename, _extension)


@csrf_exempt
def submission(request):
    if request.method == "POST":
        form = SubmissionForm(request.POST)
        if form.is_valid():
            image, _ = get_image_from_data_url(form.cleaned_data["image"])

            submission = ViolationSubmission(
                image=image,
                location=Point(
                    float(form.cleaned_data["longitude"]), float(form.cleaned_data["latitude"])
                ),
                captured_at=form.cleaned_data["datetime"],
            )
            submission.save()
            return redirect(
                reverse("violation_submission_review", kwargs={"submission_id": submission.id})
            )

    form = SubmissionForm()
    return render(request, "lazer.html", {"form": form})


@csrf_exempt
@transaction.non_atomic_requests
async def submission_api(request):
    if request.method == "POST":
        form = SubmissionForm(request.POST)
        if form.is_valid():
            image, _ = get_image_from_data_url(form.cleaned_data["image"])

            submission = ViolationSubmission(
                image=image,
                location=Point(
                    float(form.cleaned_data["longitude"]), float(form.cleaned_data["latitude"])
                ),
                captured_at=form.cleaned_data["datetime"],
            )
            await submission.asave()
            await submission.arefresh_from_db()

            data, addresses = await asyncio.gather(
                read_plate(
                    form.cleaned_data["image"].split(";base64,")[1],
                    datetime.datetime.now(datetime.timezone.utc),
                ),
                reverse_geocode_point(
                    f"{form.cleaned_data['latitude']}, {form.cleaned_data['longitude']}",
                    exactly_one=False,
                ),
            )

            vehicle = data.get("results", [])
            return JsonResponse(
                {
                    "vehicles": sorted(
                        vehicle, key=lambda x: x.get("vehicle", {}).get("score", 0), reverse=True
                    )[:4],
                    "addresses": [address.address for address in addresses],
                    "address": addresses[0].address,
                    "timestamp": form.cleaned_data["datetime"],
                    "submissionId": submission.submission_id,
                },
                status=200,
            )
        else:
            return JsonResponse({}, status=400)


@csrf_exempt
@transaction.non_atomic_requests
async def report_api(request):
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            image, _ = get_image_from_data_url(form.cleaned_data["image"])
            submission = await ViolationSubmission.objects.filter(
                submission_id=form.cleaned_data["submission_id"]
            ).afirst()
            if submission is None:
                return JsonResponse(
                    {"submitted": False, "error": "Reports must have a valid submission_id"},
                    status=400,
                )

            mobility_access_violation = MobilityAccessViolation(
                make=form.cleaned_data["make"],
                model=form.cleaned_data["model"],
                body_style=form.cleaned_data["body_style"],
                vehicle_color=form.cleaned_data["vehicle_color"],
                violation_observed=form.cleaned_data["violation_observed"],
                occurrence_frequency=form.cleaned_data["occurrence_frequency"],
                additional_information=form.cleaned_data["additional_information"],
                date_time_observed=None,
                _date_observed=form.cleaned_data["date_observed"],
                _time_observed=form.cleaned_data["time_observed"],
                address=None,
                _block_number=form.cleaned_data["block_number"],
                _street_name=form.cleaned_data["street_name"],
                _zip_code=form.cleaned_data["zip_code"],
            )

            async with TemporaryDirectory() as temp_dir:
                violation = await submit_form_with_playwright(
                    submission=submission,
                    violation=mobility_access_violation,
                    photo=image,
                    screenshot_dir=temp_dir,
                )
                await violation.asave()

            return JsonResponse(
                {
                    "submitted": True,
                },
                status=200,
            )
        else:
            return JsonResponse({"submitted": False}, status=400)


@transaction.non_atomic_requests
async def review(request, submission_id):
    submission = await aget_object_or_404(ViolationSubmission, id=submission_id)
    data = await read_plate(submission.image, datetime.datetime.now(datetime.timezone.utc))
    from pprint import pprint as pp

    pp(data)
    return render(request, "lazer_success.html", {"submission": submission})


def map(request):
    pins = []
    for report in ViolationReport.objects.select_related("submission").all():
        lat, lng = (report.submission.location.y, report.submission.location.x)
        pins.append([lat, lng, 1])
    return render(request, "heatmap.html", {"pins_json": json.dumps(pins)})
