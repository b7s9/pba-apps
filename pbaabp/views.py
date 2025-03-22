import sesame.utils
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView

from pbaabp.email import send_email_message
from pbaabp.forms import EmailLoginForm
from profiles.tasks import add_mailjet_subscriber


class EmailLoginView(FormView):
    template_name = "email_login.html"
    form_class = EmailLoginForm

    def get_user(self, email):
        """Find the user with this email address."""
        User = get_user_model()
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def create_link(self, user):
        """Create a login link for this user."""
        link = reverse("sesame_login")
        link = self.request.build_absolute_uri(link)
        link += sesame.utils.get_query_string(user)
        return link

    def send_email(self, user, link):
        """Send an email with this login link to this user."""
        subject = f"Login link for {self.request.get_host()}"
        message = f"""
Hello {user.first_name},

You requested that we send you a link to log in to our app:

* [Login Now]({link})

Thank you for being a part of the action!
        """
        send_email_message(None, None, [user.email], None, message=message, subject=subject)

    def email_submitted(self, email):
        user = self.get_user(email)
        if user is None:
            # Ignore the case when no user is registered with this address.
            # Possible improvement: send an email telling them to register.
            print("user not found:", email)
            return
        link = self.create_link(user)
        self.send_email(user, link)

    def form_valid(self, form):
        self.email_submitted(form.cleaned_data["email"])
        return render(self.request, "email_login_success.html")


@csrf_exempt
def newsletter_bridge(request):
    if settings.MAILJET_SECRET_SIGNUP_URL is None:
        raise Http404()

    name = request.POST.get("Name")
    email = request.POST.get("Email")

    errors = []
    if email is None:
        errors.append("Email is not provided")
    if name is None:
        errors.append("Name is not provided")
    if errors:
        raise SuspiciousOperation(f"Errors: {','.join(errors)}")

    first_name, _, last_name = name.partition(" ")
    add_mailjet_subscriber.delay(email, first_name, last_name, name)
    return HttpResponse("OK")
