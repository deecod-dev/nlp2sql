from django.apps import AppConfig


class DataQueryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dataquery"

    def ready(self):
        import dataquery.signals  # Ensure signals are connected