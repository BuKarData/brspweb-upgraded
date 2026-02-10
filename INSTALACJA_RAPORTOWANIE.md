# 🏢 Braspol - Zautomatyzowany System Raportowania Cen Mieszkań

## 📋 Opis rozwiązania

Kompletne rozwiązanie do automatycznego raportowania cen ofertowych mieszkań zgodnie z **art. 19a i 19b ustawy z dnia 21 maja 2025 r.** o zmianie ustawy o ochronie praw nabywcy lokalu mieszkalnego (Dz. U. 2025 poz. 758).

### ✅ Funkcjonalności

- **Automatyczne generowanie raportów** - codziennie o 6:00 rano
- **Pełna zgodność z ustawą** - wszystkie wymagane pola i formaty
- **Sumy kontrolne MD5** - dla każdego pliku
- **Publiczne API** - dostęp do danych w formatach CSV, JSON-LD, XLSX, XML
- **Panel administracyjny** - na stronie głównej z podglądem statusu
- **Ręczne generowanie** - możliwość natychmiastowej aktualizacji

## 🚀 Co zostało dodane do Twojego projektu

### 1. Nowy Management Command: `raportuj_auto.py`

Lokalizacja: `/oferty/management/commands/raportuj_auto.py`

**Funkcje:**
- Generuje CSV z cenami mieszkań zgodnie z ustawą
- Tworzy metadata.xml w standardzie DCAT-AP
- Generuje JSON-LD według schema.org
- Tworzy pliki XLSX
- Automatycznie oblicza i zapisuje sumy MD5
- Opcjonalnie wysyła powiadomienia na dane.gov.pl

**Użycie:**
```bash
python manage.py raportuj_auto
```

### 2. Rozszerzone API

**Nowe endpointy:**
- `/api/data.csv` - dane CSV
- `/api/data.csv.md5` - suma kontrolna CSV
- `/api/data.jsonld` - dane JSON-LD
- `/api/data.jsonld.md5` - suma kontrolna JSON-LD
- `/api/data.xlsx` - dane Excel
- `/api/data.xlsx.md5` - suma kontrolna XLSX
- `/api/metadata.xml` - metadane DCAT-AP
- `/api/metadata.xml.md5` - suma kontrolna XML

### 3. Ulepszona strona główna

**Nowe elementy:**
- Panel administracyjny na górze strony
- Bezpośrednie linki do wszystkich endpointów API
- Przycisk do ręcznego generowania raportu
- Informacje o automatycznej aktualizacji

### 4. Skrypt automatyzacji

Lokalizacja: `/scripts/daily_report.sh`

Skrypt do uruchomienia przez cron.

## 📦 Instalacja i wdrożenie

### Krok 1: Aktualizacja kodu

```bash
# Pobierz nowe pliki do swojego projektu
# Pliki do skopiowania:
# - oferty/management/commands/raportuj_auto.py
# - oferty/api.py (zaktualizowany)
# - oferty/urls.py (zaktualizowany)
# - oferty/templates/home_new.html (nowy szablon)
# - scripts/daily_report.sh

# Zastąp stary home.html nowym
mv oferty/templates/home.html oferty/templates/home_old.html
mv oferty/templates/home_new.html oferty/templates/home.html
```

### Krok 2: Pierwsze uruchomienie

```bash
# Wygeneruj pierwsze raporty
python manage.py raportuj_auto
```

Powinno utworzyć:
- `/raporty/` - katalog z raportami dzienn ymi
- `/oferty/templates/api/metadata.xml` - plik metadanych
- Wszystkie pliki `.md5`

### Krok 3: Konfiguracja automatyzacji na Railway

Railway nie wspiera bezpośrednio cron jobs, ale możemy użyć **schedulera w Django**:

#### Opcja A: Django APScheduler (zalecane)

1. Dodaj do `requirements.txt`:
```
apscheduler==3.10.4
```

2. Utwórz `oferty/scheduler.py`:
```python
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # Codziennie o 6:00 rano
    scheduler.add_job(
        lambda: call_command('raportuj_auto'),
        'cron',
        hour=6,
        minute=0,
        id='daily_report'
    )
    
    scheduler.start()
```

3. W `nieruchomosci/settings.py` dodaj na końcu:
```python
# Automatyczne raportowanie
from oferty.scheduler import start_scheduler
start_scheduler()
```

#### Opcja B: Railway Cron (za pomocą zewnętrznego serwisu)

1. Użyj [cron-job.org](https://cron-job.org)
2. Utwórz endpoint w Django do wywoływania raportu:

```python
# W oferty/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.management import call_command
import os

@csrf_exempt
def trigger_report(request):
    # Zabezpieczenie - sprawdź token
    token = request.GET.get('token', '')
    expected_token = os.getenv('REPORT_TOKEN', 'your-secret-token')
    
    if token != expected_token:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        call_command('raportuj_auto')
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

3. Dodaj URL:
```python
path('api/trigger-report/', trigger_report, name='trigger-report'),
```

4. W Railway ustaw zmienną środowiskową:
```
REPORT_TOKEN=twoj-tajny-token-12345
```

5. Na cron-job.org ustaw zadanie:
```
URL: https://www.braspol.pl/api/trigger-report/?token=twoj-tajny-token-12345
Czas: Codziennie o 6:00
```

## 🔧 Konfiguracja opcjonalna

### Wysyłka na dane.gov.pl

Jeśli chcesz automatycznie powiadamiać dane.gov.pl o aktualizacjach:

1. Skontaktuj się z administratorami portalu dane.gov.pl
2. Uzyskaj klucz API
3. W Railway dodaj zmienne środowiskowe:
```
DANE_GOV_PL_API_ENDPOINT=https://dane.gov.pl/api/submissions
DANE_GOV_PL_API_KEY=twoj-klucz-api
```

Uwaga: API dane.gov.pl może mieć inną strukturę - powyższy przykład jest uproszczony.

## 📊 Weryfikacja działania

### Sprawdź czy wszystko działa:

1. **Wejdź na stronę główną**
   - Rozwiń panel administracyjny u góry
   - Sprawdź czy wszystkie linki działają

2. **Przetestuj API:**
```bash
curl https://www.braspol.pl/api/data.csv
curl https://www.braspol.pl/api/data.csv.md5
curl https://www.braspol.pl/api/metadata.xml
```

3. **Sprawdź sumy MD5:**
```bash
# Pobierz plik i MD5
curl https://www.braspol.pl/api/data.csv > test.csv
curl https://www.braspol.pl/api/data.csv.md5 > test.md5

# Sprawdź czy się zgadzają
md5sum test.csv
cat test.md5
```

## 🔐 Zgodność z ustawą

### Wymagania ustawy vs. Implementacja

| Wymóg ustawy | Status | Implementacja |
|--------------|--------|---------------|
| Codzienne przekazywanie danych | ✅ | Automatyczne o 6:00 |
| Format zgodny z otwartymi danymi | ✅ | CSV, JSON-LD, XML |
| Metadane DCAT | ✅ | metadata.xml |
| Cena za m² | ✅ | Automatycznie obliczane |
| Pomieszczenia przynależne | ✅ | Osobne pola w CSV |
| Inne świadczenia pieniężne | ✅ | Suma innych świadczeń |
| Publiczny dostęp | ✅ | API bez autentykacji |
| Integralność danych | ✅ | Sumy MD5 |

### Pola w raporcie zgodne z ustawą:

**Dane dewelopera:**
- NIP, REGON, nazwa firmy
- Adres siedziby (województwo, powiat, gmina, miejscowość, ulica, kod pocztowy, kraj)
- Kontakt (telefon, email, strona www)

**Dane oferty:**
- ID przedsięwzięcia, nazwa przedsięwzięcia, adres
- Numer lokalu, rodzaj lokalu
- Powierzchnia użytkowa m²
- Cena lokalu brutto (PLN)
- Cena za m² brutto (PLN)
- Cena pomieszczeń przynależnych (PLN)
- Inne świadczenia pieniężne (PLN)
- Data aktualizacji

## 📝 Ręczne zarządzanie

### Wygeneruj raport ręcznie:
```bash
python manage.py raportuj_auto
```

### Sprawdź wygenerowane pliki:
```bash
ls -lh raporty/
ls -lh oferty/templates/api/
```

### Usuń stare raporty:
```bash
find raporty/ -name "*.csv" -mtime +30 -delete  # Starsze niż 30 dni
find raporty/ -name "*.xlsx" -mtime +30 -delete
find raporty/ -name "*.jsonld" -mtime +30 -delete
```

## 🆘 Troubleshooting

### Problem: Brak plików MD5
**Rozwiązanie:** Uruchom `python manage.py raportuj_auto`

### Problem: Błąd przy generowaniu CSV
**Rozwiązanie:** Sprawdź czy wszystkie oferty mają ceny:
```python
python manage.py shell
from oferty.models import Oferta
Oferta.objects.filter(ceny__isnull=True)
```

### Problem: metadata.xml nie istnieje
**Rozwiązanie:** 
```bash
mkdir -p oferty/templates/api
python manage.py raportuj_auto
```

### Problem: Cron nie działa na Railway
**Rozwiązanie:** Użyj opcji B (zewnętrzny cron-job.org) lub dodaj APScheduler

## 📞 Kontakt techniczny

W razie pytań lub problemów:
- Email: braspol@onet.pl
- Tel: +48 502 930 015

## 📄 Licencja danych

Zgodnie z ustawą, dane publikowane są jako **otwarte dane** na licencji CC0 1.0.

---

**Ostatnia aktualizacja:** 2025-02-09
**Wersja dokumentacji:** 1.0
