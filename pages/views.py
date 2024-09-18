from django.shortcuts import redirect, render


def index(request):
    if request.user.is_authenticated:
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
