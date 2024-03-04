import stripe
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from djstripe.models import Customer, PaymentMethod, Price, Product, Subscription

from membership.forms import RecurringDonationSetupForm
from membership.models import DonationTier
from profiles.forms import BaseProfileSignupForm
from profiles.models import Profile

_CUSTOM_FIELDS = [
    {
        "key": "full_name",
        "label": {"type": "custom", "custom": "Full Name, as you want us to address you"},
        "type": "text",
        "text": {"maximum_length": 128},
    },
    {
        "key": "council_district",
        "label": {"type": "custom", "custom": "Council District"},
        "type": "dropdown",
        "dropdown": {
            "options": [{"label": d[1], "value": d[0]} for d in Profile.District.choices]
        },
    },
    {
        "key": "newsletter_opt_in",
        "label": {"type": "custom", "custom": "Newsletter Opt In"},
        "type": "dropdown",
        "dropdown": {"options": [{"label": "Yes", "value": 1}, {"label": "No", "value": 0}]},
    },
]


@csrf_exempt
def create_checkout_session(request, price_id=None):
    if request.method == "POST":
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer = None
        if request.user.is_authenticated:
            customer, _ = Customer.get_or_create(request.user)
        session = stripe.checkout.Session.create(
            ui_mode="embedded",
            mode="subscription" if price_id is not None else "setup",
            currency="USD",
            line_items=[{"price": price_id, "quantity": 1}] if price_id is not None else None,
            return_url=request.build_absolute_uri(reverse("complete_checkout_session")),
            customer=customer.id if customer else None,
            custom_fields=_CUSTOM_FIELDS if customer is None else None,
        )
        request.session["_stripe_checkout_session_id"] = session.id
        return JsonResponse({"clientSecret": session.client_secret})
    else:
        context = {"stripe_public_key": settings.STRIPE_PUBLIC_KEY, "price_id": price_id}
        return TemplateResponse(request, "checkout_session.html", context)


@csrf_exempt
def create_setup_session(request):
    if request.method == "POST":
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer = None
        if request.user.is_authenticated:
            customer, _ = Customer.get_or_create(request.user)
        session = stripe.checkout.Session.create(
            ui_mode="embedded",
            mode="setup",
            currency="USD",
            return_url=request.build_absolute_uri(reverse("complete_checkout_session")),
            customer=customer.id,
        )
        request.session["_stripe_checkout_session_id"] = session.id
        return JsonResponse({"clientSecret": session.client_secret})
    else:
        context = {"stripe_public_key": settings.STRIPE_PUBLIC_KEY}
        return TemplateResponse(request, "setup_session.html", context)


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
            if not request.user.is_authenticated:
                custom_fields = {d["key"]: d[d["type"]]["value"] for d in session["custom_fields"]}
                first_name, _, last_name = custom_fields["full_name"].partition(" ")
                if last_name == "":
                    last_name = "Unknown"
                email = session["customer_details"]["email"]
                zip_code = session["customer_details"]["address"]["postal_code"]
                council_district = int(custom_fields["council_district"])
                newsletter_opt_in = bool(int(custom_fields["newsletter_opt_in"]))
                form = BaseProfileSignupForm(
                    {
                        "email": email,
                        "username": email,
                        "password1": "Password@99",
                        "password2": "Password@99",
                        "first_name": first_name,
                        "last_name": last_name,
                        "council_district": council_district,
                        "zip_code": zip_code,
                        "newsletter_opt_in": newsletter_opt_in,
                    }
                )
                if form.is_valid():
                    user = form.save(request)
                    user.set_unusable_password()
                    user.save()
                    stripe_customer = stripe.Customer.retrieve(subscription.customer.id)
                    customer = Customer._get_or_retrieve(stripe_customer["id"])
                    customer.subscriber = user
                    customer.save()
                    login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
            payment_method = subscription.default_payment_method
            if subscription.customer.default_payment_method is None:
                subscription.customer.add_payment_method(payment_method, set_default=True)
    return redirect("profile")


@csrf_exempt
def create_one_time_donation_checkout_session(request):
    product = Product.objects.filter(name="One-Time Donation", active=True).first()
    if product is None:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_product_search = stripe.Product.search(
            query="active:'true' AND name:'One-Time Donation'"
        )
        if len(stripe_product_search["data"]) > 1:
            raise LookupError("Incorrect number of stripe products found")
        if len(stripe_product_search["data"]) < 1:
            stripe_product = stripe.Product.create(
                name="One-Time Donation",
                active=True,
                description=(
                    "One-Time Donation to Philly Bike Action, "
                    "a registered charity in The Commonwealth of Pennsylvania. "
                    "Contributions to Philly Bike Action are not deductible "
                    "as charitable contributions for federal income tax purposes."
                ),
                shippable=False,
                statement_descriptor="Philly Bike Action",
            )
        else:
            stripe_product = stripe.Product.retrieve(stripe_product_search["data"][0]["id"])

        product = Product()._get_or_retrieve(stripe_product.id)

    price = Price.objects.filter(product=product, unit_amount=None, type="one_time").first()
    if price is None:
        price_search = [
            p
            for p in stripe.Price.search(query=f"product:'{stripe_product.id}'")["data"]
            if p.get("type", None) == "one_time" and p.get("custom_unit_amount", None) is not None
        ]
        if len(price_search) > 1:
            raise LookupError("Incorrect number of stripe prices found")
        elif len(price_search) < 1:
            price = Price.create(
                product=product,
                currency="USD",
                custom_unit_amount={
                    "enabled": True,
                    "preset": 2500,
                    "minimum": 1000,
                    "maximum": 100000,
                },
                unit_amount=None,
            )
        else:
            price = Price()._get_or_retrieve(price_search[0]["id"])

    if request.method == "POST":
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            ui_mode="embedded",
            mode="payment",
            currency="USD",
            line_items=[{"price": price.id, "quantity": 1}],
            return_url=request.build_absolute_uri(
                reverse("complete_one_time_donation_checkout_session")
            ),
            customer=(
                request.user.djstripe_customers.first().id
                if request.user.is_authenticated and request.user.djstripe_customers.first()
                else None
            ),
        )
        request.session["_stripe_checkout_session_id"] = session.id
        return JsonResponse({"clientSecret": session.client_secret})
    else:
        context = {"stripe_public_key": settings.STRIPE_PUBLIC_KEY}
        return TemplateResponse(request, "checkout_session.html", context)


def complete_one_time_donation_checkout_session(request):
    checkout_session_id = request.session.pop("_stripe_checkout_session_id", default=None)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.retrieve(checkout_session_id)
    if session["status"] == "complete":
        return redirect("index")
    return redirect("index")


@login_required
def card_remove(request, payment_method_id):
    method = PaymentMethod.objects.filter(id=payment_method_id).first()
    if method is not None:
        method.detach()
    return redirect("profile")


@login_required
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


@login_required
def cancel_recurring_donation(request, subscription_id=None):
    subscription = Subscription.objects.filter(id=subscription_id).first()
    if subscription is not None:
        subscription.cancel()
    return redirect("profile")


@login_required
def change_recurring_donation(request, subscription_id=None):
    subscription = Subscription.objects.filter(id=subscription_id).first()
    if request.method == "POST":
        if subscription is not None:
            form = RecurringDonationSetupForm(request.POST)
            if form.is_valid():
                donation_tier = DonationTier.objects.get(id=form.cleaned_data["donation_tier"])
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe_subscription = stripe.Subscription.retrieve(subscription.id)
            stripe.SubscriptionItem.modify(
                stripe_subscription["items"]["data"][0]["id"],
                price=donation_tier.stripe_price.id,
                proration_behavior="none",
            )
            stripe_subscription = stripe.Subscription.retrieve(subscription.id)
            subscription = Subscription.sync_from_stripe_data(stripe_subscription)
            return redirect("profile")
    else:
        form = RecurringDonationSetupForm()
        context = {"form": form}
        return TemplateResponse(request, "change_recurring_donation.html", context)
