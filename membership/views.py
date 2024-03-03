import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from djstripe.models import Customer, PaymentMethod, Subscription

from membership.forms import RecurringDonationSetupForm
from membership.models import DonationTier


@csrf_exempt
def create_checkout_session(request, price_id=None):
    if request.method == "POST":
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer, _ = Customer.get_or_create(request.user)
        session = stripe.checkout.Session.create(
            ui_mode="embedded",
            mode="subscription" if price_id is not None else "setup",
            currency="USD",
            line_items=[{"price": price_id, "quantity": 1}] if price_id is not None else None,
            return_url=request.build_absolute_uri(reverse("complete_checkout_session")),
            customer=customer.id,
        )
        request.session["_stripe_checkout_session_id"] = session.id
        return JsonResponse({"clientSecret": session.client_secret})
    else:
        context = {"stripe_public_key": settings.STRIPE_PUBLIC_KEY, "price_id": price_id}
        return TemplateResponse(request, "checkout_session.html", context)


def complete_checkout_session(request):
    checkout_session_id = request.session.pop("_stripe_checkout_session_id", default=None)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.retrieve(checkout_session_id)
    if session["status"] == "complete":
        if session.get("setup_intent", None):
            setup_intent = stripe.SetupIntent.retrieve(session["setup_intent"])
            payment_method = PaymentMethod._get_or_retrieve(setup_intent["payment_method"])
        elif session.get("subscription", None):
            subscription = Subscription._get_or_retrieve(session["subscription"])
            payment_method = subscription.default_payment_method
            if subscription.customer.default_payment_method is None:
                subscription.customer.add_payment_method(payment_method, set_default=True)
    return redirect("profile")


def card_remove(request, payment_method_id):
    method = PaymentMethod.objects.filter(id=payment_method_id).first()
    if method is not None:
        method.detach()
    return redirect("profile")


def card_make_default(request, payment_method_id):
    method = PaymentMethod.objects.filter(id=payment_method_id).first()
    if method is not None:
        method.customer.add_payment_method(method, set_default=True)
    return redirect("profile")


def setup_recurring_donation(request, donation_tier_id=None):
    if request.method == "POST":
        form = RecurringDonationSetupForm(request.POST)
        if form.is_valid():
            donation_tier = DonationTier.objects.get(id=form.cleaned_data["donation_tier"])
            return redirect(
                "create_subscription_checkout_session", price_id=donation_tier.stripe_price.id
            )
    else:
        form = RecurringDonationSetupForm()
        context = {"form": form}
        return TemplateResponse(request, "setup_recurring_donation.html", context)
