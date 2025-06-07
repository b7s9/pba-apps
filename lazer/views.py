import asyncio
import base64
import datetime
import secrets

from django.contrib.gis.geos import Point
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import aget_object_or_404, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt

from facets.utils import reverse_geocode_point
from lazer.forms import SubmissionForm
from lazer.integrations.platerecognizer import read_plate
from lazer.models import ViolationSubmission


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

            data, address = await asyncio.gather(
                read_plate(
                    form.cleaned_data["image"].split(";base64,")[1],
                    datetime.datetime.now(datetime.timezone.utc),
                ),
                reverse_geocode_point(
                    f"{form.cleaned_data['latitude']}, {form.cleaned_data['longitude']}"
                ),
            )
            from pprint import pprint as pp

            pp(data)
            print(address)

            vehicle = data.get("results", [])
            pp(sorted(vehicle, key=lambda x: x.get("vehicle", {}).get("score", 0), reverse=True))
            return JsonResponse(
                {
                    "vehicles": sorted(
                        vehicle, key=lambda x: x.get("vehicle", {}).get("score", 0), reverse=True
                    )[:4],
                    "address": address.address,
                    "timestamp": form.cleaned_data["datetime"],
                },
                status=200,
            )
        else:
            print(form)
            return JsonResponse({}, status=400)


@transaction.non_atomic_requests
async def review(request, submission_id):
    submission = await aget_object_or_404(ViolationSubmission, id=submission_id)
    data = await read_plate(submission.image, datetime.datetime.now(datetime.timezone.utc))
    from pprint import pprint as pp

    pp(data)
    return render(request, "lazer_success.html", {"submission": submission})
