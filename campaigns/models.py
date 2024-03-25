import uuid

from django.db import models, transaction
from django.utils.text import slugify
from markdownfield.models import RenderedMarkdownField
from markdownfield.validators import VALIDATOR_NULL

from campaigns.tasks import sync_to_wordpress
from pbaabp.models import MarkdownField


class Campaign(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active"
        COMPLETED = "completed"
        CANCELED = "canceled"
        SUSPENDED = "suspended"
        UNKNOWN = "unknown"

    class District(models.IntegerChoices):
        NO_DISTRICT = 0, "N/A - Not Philadelphia"
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
        ALL_CITY = 99, "All of Philadelphia"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=512)
    slug = models.SlugField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices)
    description = models.TextField(null=True, blank=True)
    cover = models.URLField(null=True, blank=True)

    content = MarkdownField(rendered_field="content_rendered", validator=VALIDATOR_NULL)
    content_rendered = RenderedMarkdownField()

    wordpress_id = models.CharField(max_length=64, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug = slugify(self.title)
        if not self._state.adding:
            old_model = Campaign.objects.get(pk=self.pk)
            change_fields = [
                f.name
                for f in Campaign._meta._get_fields()
                if f.name not in ["id", "wordpress_id"]
            ]
            modified = False
            for i in change_fields:
                if getattr(old_model, i, None) != getattr(self, i, None):
                    modified = True
            if modified:
                transaction.on_commit(lambda: sync_to_wordpress.delay(self.id))
        else:
            transaction.on_commit(lambda: sync_to_wordpress.delay(self.id))
        super(Campaign, self).save(*args, **kwargs)
