from django.contrib import admin
from django_tuieditor.widgets import MarkdownEditorWidget
from markdownfield.models import MarkdownField

from campaigns.models import Campaign, Petition, PetitionSignature


class CampaignAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("css/tui-editor.css",)}

    readonly_fields = ["wordpress_id"]
    formfield_overrides = {MarkdownField: {"widget": MarkdownEditorWidget}}
    autocomplete_fields = ["events"]


class PetitionAdmin(admin.ModelAdmin):
    pass


class PetitionSignatureAdmin(admin.ModelAdmin):
    list_display = ["__str__", "petition"]
    list_filter = ["petition"]
    pass


admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Petition, PetitionAdmin)
admin.site.register(PetitionSignature, PetitionSignatureAdmin)
