import os
from django.apps import AppConfig


class OfertyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "oferty"
    verbose_name = "Oferty"

    def ready(self):
        if os.environ.get("RUN_SCHEDULER", "").lower() == "true":
            from oferty.scheduler import start_scheduler
            start_scheduler()
