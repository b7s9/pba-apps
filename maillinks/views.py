import qrcode
import qrcode.image.svg
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from maillinks.models import MailLink


def maillink(request, slug):
    maillink_object = MailLink.objects.filter(slug=slug).first()
    if maillink_object is None:
        raise Http404

    response = HttpResponse(content="", status=303)
    response["Location"] = maillink_object.link

    return response


def view(request, slug):
    maillink_object = MailLink.objects.filter(slug=slug).first()
    if maillink_object is None:
        raise Http404

    return render(request, "maillink.html", context={"maillink": maillink_object})


def flyer(request, slug):
    maillink_object = MailLink.objects.filter(slug=slug).first()
    if maillink_object is None:
        raise Http404

    qrlink = request.build_absolute_uri(reverse("maillink_send", kwargs={"slug": slug}))
    qrcode_img = qrcode.make(qrlink, image_factory=qrcode.image.svg.SvgPathImage)

    return render(
        request,
        "flyer.html",
        context={"maillink": maillink_object, "qrcode": qrcode_img.to_string(encoding="unicode")},
    )
