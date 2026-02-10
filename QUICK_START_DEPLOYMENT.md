# 🚀 Szybki Start - Braspol Reporting System

## 3 kroki do uruchomienia

### 1️⃣ Push do GitHub

```bash
cd brspweb-main
git init
git add .
git commit -m "System raportowania cen mieszkań"
git remote add origin https://github.com/TWOJA-NAZWA/braspol-reporting.git
git push -u origin main
```

### 2️⃣ Deploy na Railway

1. Wejdź na [railway.app](https://railway.app)
2. Kliknij "New Project" → "Deploy from GitHub repo"
3. Wybierz `braspol-reporting`
4. Dodaj PostgreSQL: "New" → "Database" → "PostgreSQL"
5. Ustaw zmienne środowiskowe (Settings → Variables):

```env
DJANGO_SECRET_KEY=generuj-losowy-50-znakowy-klucz
DJANGO_DEBUG=False
ALLOWED_HOSTS=.railway.app,www.braspol.pl
```

### 3️⃣ Sprawdź działanie

Po deployu Railway da Ci URL (np. `twoj-projekt.up.railway.app`):

- **Strona główna:** `https://twoj-projekt.up.railway.app/`
- **API CSV:** `https://twoj-projekt.up.railway.app/api/data.csv`
- **Status:** `https://twoj-projekt.up.railway.app/system-status/`

---

## ✅ Weryfikacja

Sprawdź czy wszystko działa:

```bash
# Status systemu
curl https://twoj-projekt.up.railway.app/system-status/

# Pobierz dane CSV
curl https://twoj-projekt.up.railway.app/api/data.csv

# Suma kontrolna MD5
curl https://twoj-projekt.up.railway.app/api/data.csv.md5
```

---

## 🔧 Ręczne uruchomienie raportu

W Railway → projekt → Settings → Deploy → Custom Start Command:

```bash
python manage.py raportuj_auto && gunicorn nieruchomosci.wsgi
```

Lub uruchom ręcznie z przycisku na stronie głównej.

---

## 📊 Co dalej?

1. **Połącz domenę** - W Railway Settings → Domains dodaj `www.braspol.pl`
2. **Monitoruj** - Sprawdzaj regularnie status na stronie głównej
3. **Zgłoś do portalu** - Przekaż URL API na [dane.gov.pl](https://dane.gov.pl)

---

## ❓ Problemy?

- **Nie działa scheduler?** → Sprawdź logi w Railway
- **Brak plików?** → Kliknij "Aktualizuj teraz" na stronie głównej
- **Błąd 500?** → Sprawdź zmienne środowiskowe

Pełna dokumentacja: `README_DEPLOYMENT.md`
