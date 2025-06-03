import base64
import secrets

from django.contrib.gis.geos import Point
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt

from lazer.forms import SubmissionForm
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
            )
            submission.save()
            return redirect(
                reverse("violation_submission_review", kwargs={"submission_id": submission.id})
            )

    form = SubmissionForm()
    return render(request, "lazer.html", {"form": form})


def review(request, submission_id):
    submission = get_object_or_404(ViolationSubmission, id=submission_id)
    return render(request, "lazer_success.html", {"submission": submission})
