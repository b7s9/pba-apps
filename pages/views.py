from django.shortcuts import redirect, render


def index(request):
    if request.user.is_authenticated:
        return redirect("profile")
    return render(request, "index.html")


def donate(request):
    return render(request, "donate.html")


def brand(request):
    return render(request, "brand-guidelines.html")
