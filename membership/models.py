import uuid

from django.contrib.auth.models import User
from django.db import models, transaction
from djstripe.models import Price, Subscription
from ordered_model.models import OrderedModel

from membership.tasks import sync_donation_tier_to_stripe


class DonationTier(OrderedModel):
    class Recurrence(models.IntegerChoices):
        MONTHLY = 0, "month"
        ANNUAL = 1, "year"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stripe_price = models.ForeignKey(Price, blank=True, null=True, on_delete=models.SET_NULL)

    active = models.BooleanField(blank=False, default=False)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    recurrence = models.IntegerField(null=False, blank=False, choices=Recurrence.choices)

    def save(self, *args, **kwargs):
        if self._state.adding:
            transaction.on_commit(lambda: sync_donation_tier_to_stripe.delay(self.id))
        else:
            old_model = DonationTier.objects.get(pk=self.pk)
            change_fields = [
                f.name
                for f in DonationTier._meta._get_fields()
                if f.name not in ["id", "stripe_price"]
            ]
            modified = False
            for i in change_fields:
                if getattr(old_model, i, None) != getattr(self, i, None):
                    modified = True
            if modified:
                transaction.on_commit(lambda: sync_donation_tier_to_stripe.delay(self.id))
        super(DonationTier, self).save(*args, **kwargs)

    def __str__(self):
        return f"${self.cost}/{self.get_recurrence_display()}"


class DonationConfiguration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_subscription = models.ForeignKey(
        Subscription, blank=True, null=True, on_delete=models.SET_NULL
    )

    tier = models.ForeignKey(DonationTier, on_delete=models.CASCADE)


class Membership(models.Model):
    class Kind(models.IntegerChoices):
        FISCAL = 0, "Fiscal"
        PARTICIPATION = 1, "Participation"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    kind = models.IntegerField(null=False, blank=False, choices=Kind.choices)
