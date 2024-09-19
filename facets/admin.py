from django.contrib.gis import admin
from django.contrib.gis.db import models
from django.contrib.gis.forms.widgets import OSMWidget

from facets.models import District, RegisteredCommunityOrganization, ZipCode


class DistrictAdmin(admin.ModelAdmin):
    list_display = ["name"]

    formfield_overrides = {
        models.MultiPolygonField: {"widget": OSMWidget},
    }


class RegisteredCommunityOrganizationAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    readonly_fields = ("zip_codes",)

    formfield_overrides = {
        models.MultiPolygonField: {"widget": OSMWidget},
    }

    def zip_codes(self, obj):
        return ", ".join([z.name for z in obj.intersecting_zips.all()])


class ZipCodeAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]

    formfield_overrides = {
        models.MultiPolygonField: {"widget": OSMWidget},
    }


admin.site.register(District, DistrictAdmin)
admin.site.register(RegisteredCommunityOrganization, RegisteredCommunityOrganizationAdmin)
admin.site.register(ZipCode, ZipCodeAdmin)
