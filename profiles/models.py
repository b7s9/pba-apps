import uuid

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class Profile(models.Model):
    class District(models.IntegerChoices):
        NO_DISTRICT = 0, "N/A - I do not live in Philadelphia"
        DISTRICT_1 = 1, "District 1"
        DISTRICT_2 = 2, "District 2"
        DISTRICT_3 = 3, "District 3"
        DISTRICT_4 = 4, "District 4"
        DISTRICT_5 = 5, "District 5"
        DISTRICT_6 = 6, "District 6"
        DISTRICT_7 = 7, "District 7"
        DISTRICT_8 = 8, "District 8"
        DISTRICT_9 = 9, "District 9"
        DISTRICT_10 = 10, "District 10"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mailchimp_contact_id = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    council_district = models.IntegerField(null=False, blank=False, choices=District.choices)
    zip_code = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^(^[0-9]{5}(?:-[0-9]{4})?$|^$)",
                message="Must be a valid zipcode in formats 19107 or 19107-3200",
            )
        ],
        null=True,
        blank=True,
    )
    newsletter_opt_in = models.BooleanField(blank=False, default=False)

    @property
    def discord(self):
        return self.user.socialaccount_set.filter(provider="discord").first()

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.user.email}"
