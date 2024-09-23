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
    readonly_fields = ("zip_code_names", "zip_codes")

    formfield_overrides = {
        models.MultiPolygonField: {"widget": OSMWidget},
        ZipCode: {"widget": OSMWidget},
    }

    def zip_code_names(self, obj):
        return ", ".join(
            [
                z.name
                for z in obj.intersecting_zips.all()
                if z.mpoly.intersection(obj.mpoly).area / z.mpoly.area > 0.01
            ]
        )

    def zip_codes(self, obj):
        return obj.intersecting_zips.all()


class ZipCodeAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]

    formfield_overrides = {
        models.MultiPolygonField: {"widget": OSMWidget},
    }


admin.site.register(District, DistrictAdmin)
admin.site.register(RegisteredCommunityOrganization, RegisteredCommunityOrganizationAdmin)
admin.site.register(ZipCode, ZipCodeAdmin)
