import datetime
import uuid

from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.core.validators import RegexValidator
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from facets.models import District as DistrictFacet
from facets.models import (
    RegisteredCommunityOrganization as RegisteredCommunityOrganizationFacet,
)
from profiles.tasks import geocode_profile, sync_to_mailchimp


class Profile(models.Model):
    class District(models.IntegerChoices):
        NO_DISTRICT = 0, _("N/A - I do not live in Philadelphia")
        DISTRICT_1 = 1, _("District 1")
        DISTRICT_2 = 2, _("District 2")
        DISTRICT_3 = 3, _("District 3")
        DISTRICT_4 = 4, _("District 4")
        DISTRICT_5 = 5, _("District 5")
        DISTRICT_6 = 6, _("District 6")
        DISTRICT_7 = 7, _("District 7")
        DISTRICT_8 = 8, _("District 8")
        DISTRICT_9 = 9, _("District 9")
        DISTRICT_10 = 10, _("District 10")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mailchimp_contact_id = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    council_district = models.IntegerField(
        null=True, blank=True, choices=District.choices, verbose_name=_("Council District")
    )
    street_address = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        verbose_name=_("Street Address"),
        help_text=_(
            "Your street address will be used to determine your Philadelphia "
            "City Council District and connect you with actions "
            "you can take in your specific neighborhood."
        ),
    )
    zip_code = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^(^[0-9]{5}(?:-[0-9]{4})?$|^$)",
                message="Must be a valid zipcode in formats 19107 or 19107-3200",
            )
        ],
        null=True,
        blank=False,
        verbose_name=_("Zip Code"),
    )
    newsletter_opt_in = models.BooleanField(
        blank=False,
        default=False,
        verbose_name=_("Newsletter"),
        help_text=_("Subscribe to Philly Bike Actions monthly newsletter."),
    )

    location = models.PointField(blank=True, null=True, srid=4326)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            old_model = Profile.objects.get(pk=self.pk)
            change_fields = [
                f.name
                for f in Profile._meta._get_fields()
                if f.name in ["newsletter_opt_in", "street_address"]
            ]
            modified = False
            for i in change_fields:
                if getattr(old_model, i, None) != getattr(self, i, None):
                    modified = True
            if modified:
                transaction.on_commit(lambda: sync_to_mailchimp.delay(self.id))
                transaction.on_commit(lambda: geocode_profile.delay(self.id))
        else:
            transaction.on_commit(lambda: sync_to_mailchimp.delay(self.id))
            transaction.on_commit(lambda: geocode_profile.delay(self.id))
        super(Profile, self).save(*args, **kwargs)

    @property
    def district(self):
        if self.street_address is None:
            return None
        if self.location is None:
            return None
        return DistrictFacet.objects.filter(mpoly__contains=self.location).first()

    @property
    def rcos(self):
        if self.street_address is None:
            return None
        if self.location is None:
            return None
        return (
            RegisteredCommunityOrganizationFacet.objects.filter(mpoly__contains=self.location)
            .filter(properties__ORG_TYPE="Other")
            .order_by("properties__OBJECTID")
            .all()
        )

    @property
    def ward_rcos(self):
        if self.street_address is None:
            return None
        if self.location is None:
            return None
        return (
            RegisteredCommunityOrganizationFacet.objects.filter(mpoly__contains=self.location)
            .filter(properties__ORG_TYPE="Ward")
            .order_by("properties__OBJECTID")
            .all()
        )

    @property
    def other_rcos(self):
        if self.street_address is None:
            return None
        if self.location is None:
            return None
        return (
            RegisteredCommunityOrganizationFacet.objects.filter(mpoly__contains=self.location)
            .filter(properties__ORG_TYPE__in=["NID", "SSD", None])
            .order_by("properties__OBJECTID")
            .all()
        )

    @property
    def discord(self):
        return self.user.socialaccount_set.filter(provider="discord").first()

    @property
    def events(self):
        return [rsvp.event for rsvp in self.user.event_rsvps.all()]

    @property
    def upcoming_events(self):
        return (
            self.user.event_rsvps.filter(
                event__start_datetime__gte=datetime.datetime.now() - datetime.timedelta(hours=3)
            )
            .order_by("event__start_datetime")
            .all()
        )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.user.email}"


class ShirtInterest(models.Model):
    class Fit(models.IntegerChoices):
        ALTERNATIVE_01070C = 0, 'Unisex Classic Fit - "Go-To T-Shirt"'
        ALTERNATIVE_5114C1 = (
            1,
            "Women's Relaxed Fit - \"Women's Go-To Headliner Cropped Tee\"",
        )

    class Size(models.IntegerChoices):
        XS = -2, "XS"
        S = -1, "S"
        M = 0, "M"
        L = 1, "L"
        XL = 2, "XL"
        XXL = 3, "2XL"

    class PrintColor(models.IntegerChoices):
        PINK = 0, "Pink"
        GREEN = 1, "Green"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tshirt_requests")
    paid = models.BooleanField(default=False)
    fulfilled = models.BooleanField(default=False)

    fit = models.IntegerField(null=False, blank=False, choices=Fit.choices)
    size = models.IntegerField(null=False, blank=False, choices=Size.choices)
    print_color = models.IntegerField(null=False, blank=False, choices=PrintColor.choices)
