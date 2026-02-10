# 🚀 SZYBKI START - Automatyczne Raportowanie

## ✅ Lista rzeczy do zrobienia

### 1. Kopiuj nowe pliki do projektu ✓
```bash
# Wszystkie pliki zostały już dodane do brspweb-main/
```

### 2. Zaktualizuj szablon strony głównej

```bash
cd /twoja-sciezka/brspweb-main

# Zachowaj kopię starego szablonu
cp oferty/templates/home.html oferty/templates/home_old.html

# Użyj nowego szablonu z panelem administracyjnym
# Opcja A: Zastąp całkowicie
cp oferty/templates/home_new.html oferty/templates/home.html

# Opcja B: Ręcznie dodaj panel administracyjny do swojego szablonu
# (skopiuj sekcję <div class="admin-panel"> z home_new.html)
```

### 3. Zainstaluj zależności

```bash
pip install APScheduler==3.10.4
```

### 4. Wygeneruj pierwsze raporty

```bash
python manage.py raportuj_auto
```

Sprawdź czy utworzyły się:
- `raporty/Raport_ofert_Braspol_2025-XX-XX.csv`
- `raporty/Raport_ofert_Braspol_2025-XX-XX.csv.md5`
- `oferty/templates/api/metadata.xml`
- `oferty/templates/api/metadata.xml.md5`

### 5. Sprawdź API

Uruchom serwer:
```bash
python manage.py runserver
```

Otwórz w przeglądarce:
- http://localhost:8000/api/data.csv
- http://localhost:8000/api/data.csv.md5
- http://localhost:8000/api/metadata.xml
- http://localhost:8000/api/metadata.xml.md5

### 6. Wdróż na Railway

```bash
# Zatwierdź zmiany w git
git add .
git commit -m "Dodano automatyczne raportowanie zgodne z ustawą"
git push

# Railway automatycznie wykryje zmiany i wdroży
```

### 7. Ustaw zmienne środowiskowe na Railway (opcjonalne)

Jeśli chcesz wysyłać powiadomienia na dane.gov.pl:

W panelu Railway → Settings → Variables:
```
DANE_GOV_PL_API_ENDPOINT=https://dane.gov.pl/api/submissions
DANE_GOV_PL_API_KEY=twoj-klucz-api
```

### 8. Przetestuj po wdrożeniu

```bash
# Sprawdź czy endpointy działają
curl https://www.braspol.pl/api/data.csv
curl https://www.braspol.pl/api/data.csv.md5
curl https://www.braspol.pl/api/metadata.xml

# Sprawdź sumę MD5
curl https://www.braspol.pl/api/data.csv > test.csv
curl https://www.braspol.pl/api/data.csv.md5 > test.md5
md5sum test.csv
cat test.md5
# Powinny się zgadzać!
```

## 📌 Najważniejsze endpointy API

Wszystkie publicznie dostępne (bez autentykacji):

| Endpoint | Opis |
|----------|------|
| `/api/data.csv` | Dane w formacie CSV |
| `/api/data.csv.md5` | Suma MD5 dla CSV |
| `/api/data.jsonld` | Dane w formacie JSON-LD |
| `/api/data.jsonld.md5` | Suma MD5 dla JSON-LD |
| `/api/data.xlsx` | Dane w formacie Excel |
| `/api/data.xlsx.md5` | Suma MD5 dla Excel |
| `/api/metadata.xml` | Metadane DCAT-AP |
| `/api/metadata.xml.md5` | Suma MD5 dla XML |

## ⏰ Automatyzacja

### Automatyczne raportowanie będzie działać:
- **Codziennie o 6:00 rano** (dzięki APScheduler)
- Automatycznie przy starcie aplikacji na Railway
- Możesz też uruchomić ręcznie: `python manage.py raportuj_auto`

### Sprawdź czy scheduler działa:

Gdy uruchomisz serwer, w logach powinno pojawić się:
```
Scheduler uruchomiony - raporty będą generowane codziennie o 6:00
```

## ❗ Rozwiązywanie problemów

### Problem: Scheduler się nie uruchamia na Railway

**Rozwiązanie:** Użyj zewnętrznego crona (cron-job.org):

1. Utwórz endpoint do wyzwalania raportu:

W `oferty/views.py` dodaj:
```python
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.management import call_command
import os

@csrf_exempt
def trigger_report(request):
    token = request.GET.get('token', '')
    expected = os.getenv('REPORT_TOKEN', 'change-me')
    
    if token != expected:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        call_command('raportuj_auto')
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

W `oferty/urls.py` dodaj:
```python
path('api/trigger-report/', trigger_report, name='trigger-report'),
```

2. Ustaw zmienną w Railway:
```
REPORT_TOKEN=twoj-tajny-token-12345
```

3. Na [cron-job.org](https://cron-job.org) ustaw zadanie:
```
URL: https://www.braspol.pl/api/trigger-report/?token=twoj-tajny-token-12345
Harmonogram: Codziennie o 6:00
```

### Problem: Brak plików MD5

Uruchom: `python manage.py raportuj_auto`

### Problem: metadata.xml nie istnieje

```bash
mkdir -p oferty/templates/api
python manage.py raportuj_auto
```

## 📞 Potrzebujesz pomocy?

- Email: braspol@onet.pl
- Tel: +48 502 930 015

## ✅ Checklist końcowy

- [ ] Zainstalowano APScheduler
- [ ] Uruchomiono `raportuj_auto` ręcznie
- [ ] Sprawdzono czy pliki się tworzą w `/raporty/`
- [ ] Sprawdzono czy `metadata.xml` istnieje
- [ ] Przetestowano wszystkie endpointy API
- [ ] Zweryfikowano sumy MD5
- [ ] Wdrożono na Railway
- [ ] Sprawdzono panel administracyjny na stronie głównej
- [ ] Ustawiono automatyzację (APScheduler lub cron-job.org)

---

**Gotowe!** 🎉

Twój system jest teraz w pełni zgodny z ustawą i automatycznie raportuje dane codziennie o 6:00.
