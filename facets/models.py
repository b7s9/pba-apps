import uuid

from django.contrib.gis.db import models


class District(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    mpoly = models.MultiPolygonField()
    properties = models.JSONField()

    targetable = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class RegisteredCommunityOrganization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    mpoly = models.MultiPolygonField()
    properties = models.JSONField()

    targetable = models.BooleanField(default=False)

    def __str__(self):
        return self.name
