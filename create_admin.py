#!/usr/bin/env python
"""
Samodzielny skrypt do tworzenia/aktualizacji superusera.
Nie zalezy od Django management command framework.
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nieruchomosci.settings')

import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Obsługa wielu wariantów nazw env vars
username = (
    os.environ.get("DJANGO_SUPERUSER_USERNAME")
    or os.environ.get("ADMIN_USERNAME")
)
password = (
    os.environ.get("DJANGO_SUPERUSER_PASSWORD")
    or os.environ.get("ADMIN_PASSWORD")
)
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

print(f"[create_admin] === DIAGNOSTYKA ===")
print(f"[create_admin] DJANGO_SUPERUSER_USERNAME = {repr(os.environ.get('DJANGO_SUPERUSER_USERNAME'))}")
print(f"[create_admin] ADMIN_USERNAME = {repr(os.environ.get('ADMIN_USERNAME'))}")
print(f"[create_admin] DJANGO_SUPERUSER_PASSWORD set: {bool(os.environ.get('DJANGO_SUPERUSER_PASSWORD'))}")
print(f"[create_admin] ADMIN_PASSWORD set: {bool(os.environ.get('ADMIN_PASSWORD'))}")
print(f"[create_admin] Resolved username: {repr(username)}")
print(f"[create_admin] Resolved password set: {bool(password)}")

try:
    all_users = list(User.objects.values_list('username', 'is_superuser', 'is_staff', 'is_active'))
    print(f"[create_admin] Istniejacy uzytkownicy: {all_users}")
except Exception as e:
    print(f"[create_admin] Blad przy listowaniu uzytkownikow: {e}")

if not username or not password:
    print("[create_admin] BRAK username lub password w env vars - pomijam.")
    print("[create_admin] Ustaw DJANGO_SUPERUSER_USERNAME i DJANGO_SUPERUSER_PASSWORD na Railway.")
    sys.exit(0)

try:
    user = User.objects.filter(username=username).first()
    if user:
        print(f"[create_admin] Uzytkownik '{username}' istnieje - aktualizuje haslo i uprawnienia...")
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        if email:
            user.email = email
        user.save()
        print(f"[create_admin] SUKCES: Haslo zaktualizowane dla '{username}'.")
    else:
        print(f"[create_admin] Uzytkownik '{username}' nie istnieje - tworze...")
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"[create_admin] SUKCES: Superuser '{username}' utworzony!")

    # Weryfikacja
    user = User.objects.get(username=username)
    print(f"[create_admin] Weryfikacja: is_superuser={user.is_superuser}, is_staff={user.is_staff}, is_active={user.is_active}")
    print(f"[create_admin] Weryfikacja: has_usable_password={user.has_usable_password()}")

except Exception as e:
    print(f"[create_admin] BLAD: {e}")
    import traceback
    traceback.print_exc()
