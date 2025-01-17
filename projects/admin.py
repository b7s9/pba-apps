from django.contrib import admin

from projects.models import ProjectApplication


class ProjectApplicationAdmin(admin.ModelAdmin):
    pass


admin.site.register(ProjectApplication, ProjectApplicationAdmin)
