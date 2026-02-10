import os
import sys
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Tworzy superusera z env vars jesli nie istnieje"

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

        self.stderr.write(f"[ensure_superuser] USERNAME env set: {bool(username)}")
        self.stderr.write(f"[ensure_superuser] PASSWORD env set: {bool(password)}")

        if not username or not password:
            self.stderr.write(self.style.WARNING(
                "[ensure_superuser] DJANGO_SUPERUSER_USERNAME or DJANGO_SUPERUSER_PASSWORD not set, skipping."
            ))
            return

        try:
            if User.objects.filter(username=username).exists():
                self.stderr.write(f"[ensure_superuser] Superuser '{username}' already exists.")
                return

            User.objects.create_superuser(username=username, email=email, password=password)
            self.stderr.write(self.style.SUCCESS(
                f"[ensure_superuser] Superuser '{username}' created successfully!"
            ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f"[ensure_superuser] ERROR creating superuser: {e}"
            ))
            # Don't raise - let gunicorn start anyway
