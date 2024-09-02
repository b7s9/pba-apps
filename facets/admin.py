from django.contrib.gis import admin
from django.contrib.gis.db import models
from django.contrib.gis.forms.widgets import OSMWidget

from facets.models import District, RegisteredCommunityOrganization


class DistrictAdmin(admin.ModelAdmin):
    list_display = ["name"]

    formfield_overrides = {
        models.MultiPolygonField: {"widget": OSMWidget},
    }


class RegisteredCommunityOrganizationAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]

    formfield_overrides = {
        models.MultiPolygonField: {"widget": OSMWidget},
    }


admin.site.register(District, DistrictAdmin)
admin.site.register(RegisteredCommunityOrganization, RegisteredCommunityOrganizationAdmin)
