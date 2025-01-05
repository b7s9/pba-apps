from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from projects.forms import ProjectApplicationForm


@login_required
def project_application(request):
    profile_complete = request.user.profile.complete
    apps_connected = request.user.profile.apps_connected

    if not profile_complete:
        message = (
            "Your profile must be complete and "
            "you must connect your discord account "
            "to submit a project application."
        )
        messages.add_message(request, messages.ERROR, message)
        return redirect("profile")

    if not apps_connected:
        message = "You must connect your discord account " "to submit a project application."
        messages.add_message(request, messages.ERROR, message)
        return redirect("profile")

    form = ProjectApplicationForm(label_suffix="")
    return render(request, "project_application_form.html", {"form": form})
