from django.apps import AppConfig


class NeighborhoodSelectionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "neighborhood_selection"

    def ready(self):
        from . import signals  # noqa: F401
