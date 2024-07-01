from django.contrib import admin

from maillinks.models import MailLink


class MailLinkAdmin(admin.ModelAdmin):
    pass


admin.site.register(MailLink, MailLinkAdmin)
