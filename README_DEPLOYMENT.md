# 🏢 Braspol - Zautomatyzowany System Raportowania Cen Mieszkań

## 📋 Nowości i usprawnienia

### ✨ Co zostało dodane:

1. **Endpointy API z sumami kontrolnymi MD5**
   - `/api/data.csv` + `/api/data.csv.md5`
   - `/api/data.jsonld` + `/api/data.jsonld.md5`
   - `/api/data.xlsx` + `/api/data.xlsx.md5`
   - `/api/metadata.xml` + `/api/metadata.xml.md5`

2. **Endpoint statusu systemu**
   - `/system-status/` - JSON z informacją o dostępności plików i liczbie ofert

3. **Ulepszona strona główna**
   - Dashboard z informacjami o systemie raportowania
   - Status dostępności danych w czasie rzeczywistym
   - Linki do wszystkich formatów danych
   - Przycisk ręcznej aktualizacji

4. **Automatyzacja zgodna z ustawą**
   - Codzienne raporty o 6:00 rano
   - Format zgodny z art. 19a i 19b ustawy
   - Wszystkie wymagane formaty (CSV, XML, JSON-LD, XLSX)

---

## 🚀 Wdrożenie na Railway

### Krok 1: Przygotowanie repozytorium

```bash
# Wejdź do folderu projektu
cd brspweb-main

# Zainicjuj repozytorium Git (jeśli jeszcze nie zrobione)
git init

# Dodaj wszystkie pliki
git add .

# Commit
git commit -m "Dodano system automatycznego raportowania zgodny z ustawą"

# Połącz z GitHub
git remote add origin https://github.com/twoj-username/braspol-reporting.git
git branch -M main
git push -u origin main
```

### Krok 2: Deploy na Railway

1. **Zaloguj się na [railway.app](https://railway.app)**

2. **Utwórz nowy projekt**
   - Kliknij "New Project"
   - Wybierz "Deploy from GitHub repo"
   - Autoryzuj Railway do dostępu do GitHub
   - Wybierz repozytorium `braspol-reporting`

3. **Railway automatycznie wykryje Django**
   - Railway wykryje `manage.py` i `requirements.txt`
   - Automatycznie zainstaluje zależności

4. **Skonfiguruj zmienne środowiskowe** (w Settings → Variables):

```env
# Django
DJANGO_SECRET_KEY=twoj-bezpieczny-klucz-min-50-znakow
DJANGO_DEBUG=False
ALLOWED_HOSTS=.railway.app,www.braspol.pl,braspol.pl

# Database (Railway automatycznie  doda PostgreSQL)
DATABASE_URL=postgresql://...  # Railway to ustawi automatycznie

# Opcjonalnie - API portalu rządowego
DANE_GOV_PL_API_ENDPOINT=https://dane.gov.pl/api/submissions
DANE_GOV_PL_API_KEY=twoj_klucz_api  # jeśli dostępny

# Konfiguracja CSRF (dla produkcji)
CSRF_TRUSTED_ORIGINS=https://*.railway.app,https://www.braspol.pl
```

5. **Dodaj bazę danych PostgreSQL**
   - W projekcie Railway kliknij "New"
   - Wybierz "Database" → "Add PostgreSQL"
   - Railway automatycznie połączy ją z aplikacją

6. **Uruchom migracje** (w zakładce Settings → Deploy):
   Railway automatycznie uruchomi:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

### Krok 3: Konfiguracja domeny

1. **W Railway → Settings → Domains**
   - Railway da CI darmową domenę `*.up.railway.app`
   - Możesz dodać swoją domenę `www.braspol.pl`

2. **Skonfiguruj DNS** (u swojego dostawcy domeny):
   ```
   Typ: CNAME
   Nazwa: www
   Wartość: twoj-projekt.up.railway.app
   ```

3. **SSL Certificate**
   - Railway automatycznie wygeneruje certyfikat SSL

---

## 📊 Struktura plików projektu

```
brspweb-main/
├── oferty/
│   ├── management/
│   │   └── commands/
│   │       ├── raportuj_auto.py    # Command generujący raporty
│   │       └── raportuj.py
│   ├── templates/
│   │   ├── api/
│   │   │   └── metadata.xml       # Generowany automatycznie
│   │   ├── home.html              # Strona główna (ulepszona)
│   │   └── home_backup.html       # Backup oryginału
│   ├── api.py                     # Endpointy API + MD5
│   ├── views.py                   # Dodano system_status()
│   ├── urls.py                    # Nowe routy
│   └── scheduler.py               # Scheduler codziennych raportów
├── raporty/                       # Katalog z generowanymi raportami
├── requirements.txt
├── manage.py
└── README_DEPLOYMENT.md           # Ten plik
```

---

## 🔧 Testowanie lokalnie

```bash
# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom migracje
python manage.py migrate

# Uruchom pierwszy raport ręcznie
python manage.py raportuj_auto

# Uruchom serwer
python manage.py runserver

# Otwórz przeglądarkę
http://localhost:8000
```

### Testowanie endpointów:

```bash
# Test CSV
curl http://localhost:8000/api/data.csv

# Test MD5 dla CSV
curl http://localhost:8000/api/data.csv.md5

# Test Metadata XML
curl http://localhost:8000/api/metadata.xml

# Test statusu systemu
curl http://localhost:8000/system-status/
```

---

## 📅 Harmonogram automatyzacji

**Scheduler uruchamia się automatycznie** przy starcie aplikacji Django.

- **Codziennie o 6:00** - Automatyczne generowanie raportów
- **Formaty:** CSV, XLSX, JSON-LD, XML
- **Sumy MD5:** Generowane dla każdego pliku
- **Lokalizacja:** Dostępne przez API i zapisane w `/raporty/`

---

## 🔗 Dostępne endpointy API

| Endpoint | Opis | Format |
|----------|------|--------|
| `/api/data.csv` | Dane o cenach mieszkań | CSV |
| `/api/data.csv.md5` | Suma kontrolna CSV | Text |
| `/api/data.jsonld` | Dane w formacie JSON-LD | JSON-LD |
| `/api/data.jsonld.md5` | Suma kontrolna JSON-LD | Text |
| `/api/data.xlsx` | Dane w formacie Excel | XLSX |
| `/api/data.xlsx.md5` | Suma kontrolna XLSX | Text |
| `/api/metadata.xml` | Metadane zgodne z DCAT | XML |
| `/api/metadata.xml.md5` | Suma kontrolna XML | Text |
| `/system-status/` | Status systemu | JSON |

---

## 🎯 Zgodność z ustawą

System jest w pełni zgodny z:
- **Art. 19a** - Obowiązek prowadzenia strony internetowej z cenami
- **Art. 19b** - Przekazywanie danych ministrowi właściwemu
- **Ustawa o otwartych danych** - Format DCAT-AP, CSV, JSON-LD

### Wymagania spełnione:

✅ Automatyczne aktualizacje raz na dobę  
✅ Format CSV z wymaganymi kolumnami  
✅ Metadane XML zgodne z DCAT-AP  
✅ Sumy kontrolne MD5 dla weryfikacji  
✅ Publiczny dostęp do API  
✅ Historia zmian cen z datami  

---

## 🛠️ Rozwiązywanie problemów

### Problem: Scheduler nie uruchamia raportów

**Rozwiązanie:**
Sprawdź logi Railway i upewnij się, że scheduler jest inicjalizowany w `apps.py`:

```python
# oferty/apps.py
from django.apps import AppConfig

class OfertyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'oferty'

    def ready(self):
        from oferty.scheduler import start_scheduler
        start_scheduler()
```

### Problem: Brak plików metadata.xml

**Rozwiązanie:**
Uruchom ręcznie command:
```bash
python manage.py raportuj_auto
```

### Problem: Błąd połączenia z bazą danych

**Rozwiązanie:**
Sprawdź zmienną `DATABASE_URL` w Railway Settings → Variables

---

## 📞 Wsparcie

W razie problemów:
1. Sprawdź logi w Railway → Deployments → View Logs
2. Przetestuj lokalnie przed deploymentem
3. Upewnij się, że wszystkie zmienne środowiskowe są ustawione

---

## 📝 Licencja

Dane publikowane są jako otwarte dane zgodnie z CC0 1.0 Universal.

---

**Data utworzenia:** 2025-02-09  
**Wersja systemu:** 1.0  
**Zgodność:** Django 4.x, Python 3.8+
