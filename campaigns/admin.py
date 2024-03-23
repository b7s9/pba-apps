from django.contrib import admin
from django_tuieditor.widgets import MarkdownEditorWidget
from markdownfield.models import MarkdownField

from campaigns.models import Campaign, Petition


class CampaignAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("css/tui-editor.css",)}

    readonly_fields = ["wordpress_id"]
    formfield_overrides = {MarkdownField: {"widget": MarkdownEditorWidget}}


class PetitionAdmin(admin.ModelAdmin):
    pass


admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Petition, PetitionAdmin)
