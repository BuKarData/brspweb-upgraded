from oferty.models import Oferta
import requests
import json
from datetime import datetime, date
import csv
import os
from openpyxl import Workbook
import io

def get_deweloper_data():
    """Zwraca dane dewelopera"""
    return {
        "nip": "1250994717",
        "regon": "141371661",
        "nazwa_firmy": "BRASPOL PAWEŁ WIĘCH",
        "wojewodztwo": "MAZOWIECKIE",
        "powiat": "wołomiński",
        "gmina": "Zielonka",
        "miejscowosc": "Zielonka",
        "ulica": "Kilińskiego 92A",
        "kod_pocztowy": "05-220",
        "kraj": "Polska",
        "telefon": "502930015",
        "email": "braspol@onet.pl",
        "strona_www": "https://www.braspol.pl"
    }

def get_oferty_data():
    """Pobiera wszystkie oferty z bazy danych"""
    return Oferta.objects.prefetch_related(
        "ceny", "inwestycja", "pomieszczenia_przynalezne", "rabaty", "inne_swiadczenia"
    ).all()

def _build_flattened_records(dane_dewelopera, oferty, max_pom, max_rab, max_swi):
    """Buduje spłaszczone rekordy dla CSV i XLSX"""
    for oferta in oferty:
        ceny_list = list(oferta.ceny.all())
        ostatnia_cena = ceny_list[-1] if ceny_list else None
        cena_m2 = (
            round(float(ostatnia_cena.kwota) / float(oferta.metraz), 2)
            if ostatnia_cena and oferta.metraz else ""
        )

        rekord_csv = {
            "nip": dane_dewelopera["nip"],
            "regon": dane_dewelopera["regon"],
            "nazwa_firmy": dane_dewelopera["nazwa_firmy"],
            "wojewodztwo": dane_dewelopera.get("wojewodztwo", ""),
            "powiat": dane_dewelopera.get("powiat", ""),
            "gmina": dane_dewelopera.get("gmina", ""),
            "miejscowosc": dane_dewelopera.get("miejscowosc", ""),
            "ulica": dane_dewelopera.get("ulica", ""),
            "kod_pocztowy": dane_dewelopera.get("kod_pocztowy", ""),
            "kraj": dane_dewelopera.get("kraj", ""),
            "telefon": dane_dewelopera.get("telefon", ""),
            "email": dane_dewelopera.get("email", ""),
            "strona_www": dane_dewelopera.get("strona_www", ""),
            "id_oferty": oferta.id,
            "numer_lokalu": oferta.numer_lokalu,
            "numer_oferty": oferta.numer_oferty if hasattr(oferta, 'numer_oferty') else "",
            "rodzaj_lokalu": oferta.rodzaj_lokalu.nazwa if oferta.rodzaj_lokalu else "",
            "metraz": float(oferta.metraz) if oferta.metraz else "",
            "pokoje": oferta.pokoje,
            "status": oferta.status,
            "cena_pln": float(ostatnia_cena.kwota) if ostatnia_cena else "",
            "cena_za_m2_pln": cena_m2,
            "data_ceny": ostatnia_cena.data.isoformat() if ostatnia_cena else "",
            "inwestycja_nazwa": oferta.inwestycja.nazwa if oferta.inwestycja else "",
            "inwestycja_adres": oferta.inwestycja.adres if oferta.inwestycja else "",
            "inwestycja_id": oferta.inwestycja.id if oferta.inwestycja else "",
        }

        for i, p in enumerate(oferta.pomieszczenia_przynalezne.all()):
            rekord_csv[f"pomieszczenie przynalezne_{i+1}"] = p.nazwa
        for i, r in enumerate(oferta.rabaty.all()):
            rekord_csv[f"rabat_{i+1}"] = r.nazwa
        for i, s in enumerate(oferta.inne_swiadczenia.all()):
            rekord_csv[f"swiadczenie_{i+1}"] = s.nazwa

        yield rekord_csv

def generate_csv_data():
    """Generuje dane CSV w pamięci (dla API) z polskimi znakami"""
    dane_dewelopera = get_deweloper_data()
    oferty = get_oferty_data()
    
    if not oferty.exists():
        return ""
    
    max_pom = max((oferta.pomieszczenia_przynalezne.count() for oferta in oferty), default=0)
    max_rab = max((oferta.rabaty.count() for oferta in oferty), default=0)
    max_swi = max((oferta.inne_swiadczenia.count() for oferta in oferty), default=0)

    fieldnames = [
        "nip", "regon", "nazwa_firmy",
        "wojewodztwo", "powiat", "gmina", "miejscowosc", "ulica", "kod_pocztowy", "kraj",
        "telefon", "email", "strona_www",
        "id_oferty", "numer_lokalu", "numer_oferty", "rodzaj_lokalu",
        "metraz", "pokoje", "status", "cena_pln", "cena_za_m2_pln", "data_ceny",
        "inwestycja_nazwa", "inwestycja_adres", "inwestycja_id",
    ]
    fieldnames += [f"pomieszczenie przynalezne_{i+1}" for i in range(max_pom)]
    fieldnames += [f"rabat_{i+1}" for i in range(max_rab)]
    fieldnames += [f"swiadczenie_{i+1}" for i in range(max_swi)]

    # UŻYJ BytesIO zamiast StringIO dla lepszego handlingu encodingu
    csv_output = io.BytesIO()
    
    # UŻYJ UTF-8 z BOM dla Excel (żeby polskie znaki działały)
    csv_output.write(b'\xEF\xBB\xBF')  # UTF-8 BOM
    
    # Zapisz dane z encodingiem UTF-8
    writer = csv.writer(io.TextIOWrapper(csv_output, encoding='utf-8-sig'), delimiter=';')
    writer.writerow(fieldnames)

    for rekord in _build_flattened_records(dane_dewelopera, oferty, max_pom, max_rab, max_swi):
        row = [rekord.get(field, "") for field in fieldnames]
        writer.writerow(row)

    # Pobierz zawartość jako bytes
    csv_content = csv_output.getvalue()
    csv_output.close()
    
    # ZWRÓĆ JAKO STRING Z UTF-8
    return csv_content.decode('utf-8-sig')

def generate_xlsx_data():
    """Generuje dane XLSX w pamięci (dla API)"""
    dane_dewelopera = get_deweloper_data()
    oferty = get_oferty_data()
    
    if not oferty.exists():
        return b""
    
    max_pom = max((oferta.pomieszczenia_przynalezne.count() for oferta in oferty), default=0)
    max_rab = max((oferta.rabaty.count() for oferta in oferty), default=0)
    max_swi = max((oferta.inne_swiadczenia.count() for oferta in oferty), default=0)

    fieldnames = [
        "nip", "regon", "nazwa_firmy",
        "wojewodztwo", "powiat", "gmina", "miejscowosc", "ulica", "kod_pocztowy", "kraj",
        "telefon", "email", "strona_www",
        "id_oferty", "numer_lokalu", "numer_oferty", "rodzaj_lokalu",
        "metraz", "pokoje", "status", "cena_pln", "cena_za_m2_pln", "data_ceny",
        "inwestycja_nazwa", "inwestycja_adres", "inwestycja_id",
    ]
    fieldnames += [f"pomieszczenie przynalezne_{i+1}" for i in range(max_pom)]
    fieldnames += [f"rabat_{i+1}" for i in range(max_rab)]
    fieldnames += [f"swiadczenie_{i+1}" for i in range(max_swi)]

    wb = Workbook()
    ws = wb.active
    ws.title = "Raport ofert"
    ws.append(fieldnames)

    for rekord in _build_flattened_records(dane_dewelopera, oferty, max_pom, max_rab, max_swi):
        row = [rekord.get(field, "") for field in fieldnames]
        ws.append(row)

    xlsx_output = io.BytesIO()
    wb.save(xlsx_output)
    xlsx_content = xlsx_output.getvalue()
    xlsx_output.close()
    
    return xlsx_content

def generate_jsonld_data():
    """Generuje dane JSON-LD w pamięci (dla API) z poprawnymi polskimi znakami"""
    dane_dewelopera = get_deweloper_data()
    oferty = get_oferty_data()
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    if not oferty.exists():
        return {"@type": "Dataset", "name": "Brak ofert", "dateModified": current_date}
    
    jsonld_context = {
        "@vocab": "http://schema.org/",
        "nip": "http://purl.org/nace/NACE2/82.6",
        "regon": "http://purl.org/nace/NACE2/54.0",
        "metraz": "http://purl.org/qudt/vocab/area",
        "cena": "http://purl.org/qudt/vocab/currency",
        "dateModified": "http://purl.org/dc/terms/date",
    }

    offers = []
    
    for oferta in oferty:
        ceny_list = list(oferta.ceny.all())
        ostatnia_cena = ceny_list[-1] if ceny_list else None
        cena_m2 = (
            round(float(ostatnia_cena.kwota) / float(oferta.metraz), 2)
            if ostatnia_cena and oferta.metraz else None
        )

        pomieszczenia_przynalezne = [{"nazwa": p.nazwa, "cena": float(p.cena)} for p in oferta.pomieszczenia_przynalezne.all()]
        rabaty = [{"nazwa": r.nazwa, "wartosc": float(r.wartosc), "typ": r.typ} for r in oferta.rabaty.all()]
        inne_swiadczenia = [{"nazwa": s.nazwa, "kwota": float(s.kwota)} for s in oferta.inne_swiadczenia.all()]

        offer = {
            "@type": "Product",
            "name": f"Oferta nr {oferta.numer_oferty}",
            "description": f"Mieszkanie {oferta.pokoje}-pokojowe o metrażu {oferta.metraz} m2.",
            "offers": {
                "@type": "Offer",
                "priceCurrency": "PLN",
                "price": float(ostatnia_cena.kwota) if ostatnia_cena else None,
                "validFrom": ostatnia_cena.data.isoformat() if ostatnia_cena else None
            },
            "itemOffered": {
                "@type": "Apartment",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": oferta.inwestycja.adres if oferta.inwestycja else "",
                    "addressLocality": "Zielonka",
                },
                "numberOfRooms": oferta.pokoje,
                "floorSize": {
                    "@type": "QuantitativeValue",
                    "value": float(oferta.metraz) if oferta.metraz else None,
                    "unitCode": "m2"
                },
                "status": oferta.status
            },
            "cena_za_m2": cena_m2,
            "pomieszczenia_przynaleznie": pomieszczenia_przynalezne,
            "rabaty": rabaty,
            "inne_swiadczenia": inne_swiadczenia,
        }
        offers.append(offer)

    jsonld_data = {
        "@context": jsonld_context,
        "@type": "Dataset",
        "name": "Raport ofert deweloperskich BRASPOL Paweł Więch",
        "description": "Zestaw ofert mieszkaniowych dewelopera BRASPOL Paweł Więch",
        "dateModified": current_date,
        "publisher": {
            "@type": "Organization",
            "name": dane_dewelopera["nazwa_firmy"],
            "vatID": dane_dewelopera["nip"],
            "taxID": dane_dewelopera["regon"],
            "address": {
                "@type": "PostalAddress",
                "streetAddress": dane_dewelopera["ulica"],
                "addressLocality": dane_dewelopera["miejscowosc"],
                "addressRegion": dane_dewelopera["wojewodztwo"],
                "postalCode": dane_dewelopera["kod_pocztowy"],
                "addressCountry": dane_dewelopera["kraj"],
            },
            "telephone": dane_dewelopera.get("telefon", ""),
            "email": dane_dewelopera.get("email", ""),
            "url": dane_dewelopera.get("strona_www", "")
        },
        "offers": offers
    }
    
    return jsonld_data

# Pozostała część oryginalnej komendy (dla celów zarządzania)
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Generuje dzienny raport ofert w formatach JSONL/JSON-LD, CSV i XLSX"

    def handle(self, *args, **kwargs):
        self.stdout.write("Rozpoczynanie generowania raportów...")

        dane_dewelopera = get_deweloper_data()
        oferty = get_oferty_data()

        if not oferty.exists():
            self.stdout.write(self.style.WARNING("Nie znaleziono ofert do raportu."))
            return

        # Zapisz do plików (dla celów zarządzania)
        raporty_dir = "raporty"
        if not os.path.exists(raporty_dir):
            os.makedirs(raporty_dir)

        data_raportu = str(date.today())
        
        # Zapisz CSV
        csv_content = generate_csv_data()
        with open(f"{raporty_dir}/Raport ofert firmy Braspol_{data_raportu}.csv", "w", encoding="utf-8-sig") as f:
            f.write(csv_content)
        
        # Zapisz XLSX
        xlsx_content = generate_xlsx_data()
        with open(f"{raporty_dir}/Raport ofert firmy Braspol_{data_raportu}.xlsx", "wb") as f:
            f.write(xlsx_content)
        
        # Zapisz JSON-LD
        jsonld_content = generate_jsonld_data()
        with open(f"{raporty_dir}/raport_{data_raportu}.jsonld", "w", encoding="utf-8") as f:
            json.dump(jsonld_content, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS("Raporty zostały wygenerowane!"))