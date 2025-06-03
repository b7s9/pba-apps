from django.contrib.gis.db import models


class ViolationSubmission(models.Model):
    location = models.PointField(srid=4326)
    image = models.ImageField()
