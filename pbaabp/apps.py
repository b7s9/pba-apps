from django.apps import AppConfig


class PBAABPConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pbaabp"

    def ready(self):
        import pbaabp.signals  # noqa: F401
