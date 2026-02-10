import os
import sys
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Tworzy lub aktualizuje superusera z env vars"

    def handle(self, *args, **options):
        User = get_user_model()

        # Obsługa obu wariantów nazw env vars
        username = (
            os.environ.get("DJANGO_SUPERUSER_USERNAME")
            or os.environ.get("ADMIN_USERNAME")
        )
        password = (
            os.environ.get("DJANGO_SUPERUSER_PASSWORD")
            or os.environ.get("ADMIN_PASSWORD")
        )
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

        self.stdout.write(f"[ensure_superuser] USERNAME env set: {bool(username)}")
        self.stdout.write(f"[ensure_superuser] PASSWORD env set: {bool(password)}")

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                "[ensure_superuser] Brak DJANGO_SUPERUSER_USERNAME lub "
                "DJANGO_SUPERUSER_PASSWORD w env vars - pomijam."
            ))
            return

        try:
            user = User.objects.filter(username=username).first()
            if user:
                # Użytkownik istnieje - zaktualizuj hasło i upewnij się że jest superuserem
                user.set_password(password)
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                if email:
                    user.email = email
                user.save()
                self.stdout.write(self.style.SUCCESS(
                    f"[ensure_superuser] Zaktualizowano haslo dla '{username}'."
                ))
            else:
                # Utwórz nowego superusera
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(self.style.SUCCESS(
                    f"[ensure_superuser] Superuser '{username}' utworzony!"
                ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"[ensure_superuser] BLAD: {e}"
            ))
