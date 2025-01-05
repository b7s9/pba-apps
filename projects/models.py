import uuid

from django.contrib.auth.models import User
from django.db import models
from django.template.loader import render_to_string

from projects.forms import ProjectApplicationForm


class ProjectApplication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submitter = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    draft = models.BooleanField(default=False)

    data = models.JSONField()
    markdown = models.TextField(blank=True, null=True)

    def render_markdown(self):
        context = {field: data["value"] for field, data in self.data.items()}
        form = ProjectApplicationForm(label_suffix="")
        context["application"] = self
        context["form"] = form
        self.markdown = render_to_string("project_application.md", context)
        self.save()
