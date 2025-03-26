from django.shortcuts import redirect, render
from wagtail.models import Site

from cms.models import HomePage


def index(request, *args, **kwargs):
    if request.get_host() == "abp.bikeaction.org":
        site = Site.find_for_request(request)
        root_page = site.root_page
        page = HomePage.objects.get(id=root_page.id)
        return page.serve(request)
    elif request.user.is_authenticated:
        return redirect("profile")
    return render(request, "index.html")


def donate(request):
    return render(request, "donate.html")


def brand(request):
    return render(request, "brand-guidelines.html")


def privacy(request):
    with open("pages/templates/privacy-and-data-policy.md") as f:
        markdown = f.read()
    return render(request, "markdown.html", context={"markdown": markdown})


def conduct(request):
    with open("pages/templates/code-of-conduct.md") as f:
        markdown = f.read()
    return render(request, "markdown.html", context={"markdown": markdown})
