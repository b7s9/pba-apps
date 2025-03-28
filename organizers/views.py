from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from organizers.forms import OrganizerForm
from organizers.models import OrganizerSubmission


@login_required
def organizer_form_view(request, pk=None):
    profile_complete = request.user.profile.complete
    apps_connected = request.user.profile.apps_connected

    if not profile_complete:
        message = (
            "Your profile must be complete and "
            "you must connect your discord account "
            "to submit a organizer form."
        )
        messages.add_message(request, messages.ERROR, message)
        return redirect("profile")

    if not apps_connected:
        message = "You must connect your discord account " "to submit a organizer form."
        messages.add_message(request, messages.ERROR, message)
        return redirect("profile")

    application = get_object_or_404(OrganizerSubmission, id=pk)

    return render(request, "organizer_form_view.html", {"application": application})


@login_required
def organizer_form(request, pk=None):
    profile_complete = request.user.profile.complete
    apps_connected = request.user.profile.apps_connected

    if not profile_complete:
        message = (
            "Your profile must be complete and "
            "you must connect your discord account "
            "to submit a organizer form."
        )
        messages.add_message(request, messages.ERROR, message)
        return redirect("profile")

    if not apps_connected:
        message = "You must connect your discord account " "to submit a organizer form."
        messages.add_message(request, messages.ERROR, message)
        return redirect("profile")

    if pk:
        application = get_object_or_404(OrganizerSubmission, id=pk)
        if not application.draft:
            return redirect("organizer_form_view", pk=application.id)

    if request.method == "POST" and "save-draft" in request.POST:
        form = OrganizerForm(request.POST, label_suffix="")
        if pk:
            application = get_object_or_404(OrganizerSubmission, id=pk)
        else:
            application = OrganizerSubmission(submitter=request.user, draft=True)
        application.data = form.to_json()
        application.save()
        messages.add_message(request, messages.SUCCESS, "Form saved, but not submitted")
        return redirect("profile")

    elif request.method == "POST" and "submit-application" in request.POST:
        form = OrganizerForm(request.POST, label_suffix="")
        if form.is_valid():
            submission = OrganizerSubmission(submitter=request.user, draft=False)
            submission.data = form.to_json()
            submission.render_markdown()
            submission.save()
            if pk:
                application = OrganizerSubmission.objects.filter(id=pk)
                if application:
                    application.delete()
            messages.add_message(
                request,
                messages.SUCCESS,
                "Form submitted! You'll hear from organizers soon.",
            )
            return redirect("profile")

    else:
        if pk:
            application = get_object_or_404(OrganizerSubmission, id=pk)
            form = OrganizerForm(
                initial={k: v["value"] for k, v in application.data.items()},
                label_suffix="",
            )
        else:
            form = OrganizerForm(label_suffix="")

    return render(request, "organizer_form.html", {"form": form})
