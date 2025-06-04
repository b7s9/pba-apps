import uuid
from urllib.parse import quote, urlencode

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class MailLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(null=True, blank=True)
    active = models.BooleanField(default=False)

    # Wrapper
    title = models.CharField(max_length=512)
    description = models.TextField(null=True, blank=True)
    call_to_action_heading = models.CharField(max_length=512, null=True, blank=True)
    call_to_action = models.TextField(null=True, blank=True)

    # Email
    to = models.CharField(max_length=1024)
    cc = models.CharField(max_length=1024, blank=True, null=True)
    bcc = models.CharField(max_length=1024, blank=True, null=True)
    subject = models.CharField(max_length=512)
    body = models.TextField()

    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug = slugify(self.title)[:49]
        super(MailLink, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("maillink_view", kwargs={"slug": self.slug})

    @property
    def link(self):
        _link = "mailto:"
        _link += quote(self.to)
        _link += "?"
        params = {}
        if self.cc is not None:
            params["cc"] = self.cc
        if self.bcc is not None:
            params["bcc"] = self.bcc
        params["subject"] = self.subject
        params["body"] = self.body
        _link += urlencode(params, quote_via=quote)
        return _link
