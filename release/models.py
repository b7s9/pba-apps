import uuid

from django.db import models, transaction
from markdownfield.models import RenderedMarkdownField
from markdownfield.validators import VALIDATOR_NULL

from pbaabp.models import MarkdownField
from release.tasks import send_release_signature_confirmation


class Release(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(null=True, blank=True)

    title = models.CharField(max_length=512)

    release = MarkdownField(rendered_field="release_rendered", validator=VALIDATOR_NULL)
    release_rendered = RenderedMarkdownField()

    def __str__(self):
        return self.title


class ReleaseSignature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    release = models.ForeignKey(
        Release, to_field="id", on_delete=models.CASCADE, related_name="signatures"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    nickname = models.CharField(max_length=64, null=False, blank=False)
    legal_name = models.CharField(max_length=128, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    dob = models.DateField(null=False, blank=False)

    def save(self, *args, **kwargs):
        transaction.on_commit(lambda: send_release_signature_confirmation.delay(self.id))
        super(ReleaseSignature, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.nickname} - {self.email}"
