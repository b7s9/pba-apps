import uuid

from django.conf import settings
from django.core.mail import EmailMessage
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from campaigns.forms import PetitionSignatureForm
from campaigns.models import Campaign, Petition, PetitionSignature


def _fetch_petition_by_slug_or_id(petition_slug_or_id):
    try:
        uuid.UUID(petition_slug_or_id)
        petition_by_id = Petition.objects.filter(id=petition_slug_or_id).first()
    except ValueError:
        petition_by_id = None
    petition_by_slug = Petition.objects.filter(slug=petition_slug_or_id).first()

    if petition_by_id is not None:
        return petition_by_id
    elif petition_by_slug is not None:
        return petition_by_slug
    else:
        return None


class CampaignDetailView(DetailView):
    model = Campaign


class CampaignListView(ListView):
    model = Campaign


def sign_petition(request, petition_slug_or_id):
    petition = _fetch_petition_by_slug_or_id(petition_slug_or_id)
    if petition is None:
        raise Http404
    if request.method == "POST":
        form = PetitionSignatureForm(
            request.POST, required_fields=petition.signature_fields, petition=petition
        )
        if form.is_valid():
            # Check for existing signature
            existing_signature = PetitionSignature.objects.filter(
                email__iexact=form.instance.email
            ).first()
            form.instance.petition = petition
            form.save()
            print(form.cleaned_data)
            if petition.send_email and form.cleaned_data.get("send_email", False):
                if not existing_signature:
                    email = EmailMessage(
                        subject=petition.title,
                        body=petition.letter + "\n\n" + form.instance.comment,
                        from_email=(
                            f"{form.instance.first_name} {form.instance.last_name} "
                            f"<{settings.DEFAULT_FROM_EMAIL}>"
                        ),
                        to=petition.email_to,
                        cc=petition.email_cc,
                        reply_to=[form.instance.email],
                    )
                    email.send()
            return HttpResponseRedirect("https://bikeaction.org")
    else:
        form = PetitionSignatureForm(required_fields=petition.signature_fields, petition=petition)

    return render(request, "petition/sign.html", context={"petition": petition, "form": form})
