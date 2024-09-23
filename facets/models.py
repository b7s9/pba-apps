import uuid

from django.contrib.gis.db import models
from django.db.models import Q
from relativity.fields import L, Relationship


class District(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    mpoly = models.MultiPolygonField()
    properties = models.JSONField()

    targetable = models.BooleanField(default=True)
    contained_profiles = Relationship(
        to="profiles.profile", predicate=Q(location__within=L("mpoly"))
    )

    def __str__(self):
        return self.name


class RegisteredCommunityOrganization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    mpoly = models.MultiPolygonField()
    properties = models.JSONField()

    targetable = models.BooleanField(default=False)
    contained_profiles = Relationship(
        to="profiles.profile", predicate=Q(location__within=L("mpoly"))
    )
    intersecting_zips = Relationship(
        to="facets.zipcode", predicate=Q(mpoly__intersects=L("mpoly"))
    )

    @property
    def zips(self):
        return [
            z
            for z in self.intersecting_zips.all()
            if z.mpoly.intersection(self.mpoly).area / self.mpoly.area > 0.001
        ]

    def __str__(self):
        return self.name


class ZipCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    mpoly = models.MultiPolygonField()
    properties = models.JSONField()

    targetable = models.BooleanField(default=False)
    contained_profiles = Relationship(
        to="profiles.profile", predicate=Q(location__within=L("mpoly"))
    )
    intersecting_rcos = Relationship(
        to="facets.registeredcommunityorganization", predicate=Q(mpoly__intersects=L("mpoly"))
    )

    def __str__(self):
        return self.name
