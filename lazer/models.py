import uuid

from django.contrib.gis.db import models
from django.utils.safestring import mark_safe


class ViolationSubmission(models.Model):
    submission_id = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    captured_at = models.DateTimeField()
    location = models.PointField(srid=4326)
    image = models.ImageField(upload_to="lazer/violations")

    def image_tag(self):
        return mark_safe('<img src="%s" style="max-height: 50px;"/>' % (self.image.url))
