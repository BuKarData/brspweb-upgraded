#!/bin/bash
# Skrypt do automatycznego generowania raportów
# Uruchamiany codziennie o 6:00 rano

# Przejdź do katalogu projektu
cd /app || cd "$(dirname "$0")"

# Aktywuj środowisko wirtualne (jeśli używasz)
# source venv/bin/activate

# Uruchom management command
python manage.py raportuj_auto

# Loguj wynik
echo "[$(date)] Raport wygenerowany automatycznie" >> /var/log/braspol_reports.log
