import uuid

from django.contrib.auth.models import User
from django.db import models, transaction
from django.template.loader import render_to_string

from projects.forms import ProjectApplicationForm


class ProjectApplication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submitter = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    thread_id = models.CharField(max_length=64, null=True, blank=True)

    draft = models.BooleanField(default=False)

    data = models.JSONField()
    markdown = models.TextField(blank=True, null=True)

    def render_markdown(self):
        context = {field: data["value"] for field, data in self.data.items()}
        form = ProjectApplicationForm(label_suffix="")
        context["application"] = self
        context["form"] = form
        self.markdown = render_to_string("project_application.md", context)

    def save(self, *args, **kwargs):
        if not self.draft and not self.thread_id:
            from projects.tasks import add_new_project_message_and_thread

            transaction.on_commit(lambda: add_new_project_message_and_thread.delay(self.id))
        super(ProjectApplication, self).save(*args, **kwargs)
