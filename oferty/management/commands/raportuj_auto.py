from django.core.management.base import BaseCommand
from oferty.models import Oferta
from datetime import datetime, date
import hashlib
import csv
import json
import os
from openpyxl import Workbook
import io
import requests
from django.conf import settings
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

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
    """Pobiera wszystkie dostępne oferty z bazy danych"""
    return Oferta.objects.prefetch_related(
        "ceny", "inwestycja", "pomieszczenia_przynalezne", "rabaty", "inne_swiadczenia"
    ).filter(status="dostępne")  # Tylko dostępne mieszkania zgodnie z ustawą


def calculate_md5(content, is_binary=False):
    """Oblicza sumę kontrolną MD5 dla contentu"""
    md5_hash = hashlib.md5()
    if is_binary:
        md5_hash.update(content)
    else:
        md5_hash.update(content.encode('utf-8'))
    return md5_hash.hexdigest()


def generate_metadata_xml():
    """Generuje plik metadata.xml zgodny ze standardem DCAT-AP"""
    root = ET.Element('rdf:RDF')
    root.set('xmlns:rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    root.set('xmlns:dct', 'http://purl.org/dc/terms/')
    root.set('xmlns:dcat', 'http://www.w3.org/ns/dcat#')
    root.set('xmlns:foaf', 'http://xmlns.com/foaf/0.1/')
    root.set('xmlns:vcard', 'http://www.w3.org/2006/vcard/ns#')
    
    # Catalog
    catalog = ET.SubElement(root, 'dcat:Catalog')
    catalog.set('rdf:about', 'https://www.braspol.pl/api/')
    
    catalog_title = ET.SubElement(catalog, 'dct:title')
    catalog_title.set('xml:lang', 'pl')
    catalog_title.text = 'Katalog danych deweloperskich Braspol'
    
    catalog_publisher = ET.SubElement(catalog, 'dct:publisher')
    catalog_publisher_org = ET.SubElement(catalog_publisher, 'foaf:Organization')
    catalog_pub_name = ET.SubElement(catalog_publisher_org, 'foaf:name')
    catalog_pub_name.text = 'BRASPOL PAWEŁ WIĘCH'
    
    # Dataset
    dataset = ET.SubElement(catalog, 'dcat:dataset')
    dataset_obj = ET.SubElement(dataset, 'dcat:Dataset')
    dataset_obj.set('rdf:about', 'https://www.braspol.pl/api/dataset/ceny-mieszkan')
    
    # Tytuł
    title = ET.SubElement(dataset_obj, 'dct:title')
    title.set('xml:lang', 'pl')
    title.text = 'Ceny ofertowe mieszkań dewelopera Braspol - Paweł Więch'
    
    # Opis
    description = ET.SubElement(dataset_obj, 'dct:description')
    description.set('xml:lang', 'pl')
    description.text = ('Zbiór danych zawierający aktualne ceny ofertowe mieszkań oferowanych przez '
                       'dewelopera BRASPOL Paweł Więch zgodnie z art. 19a i 19b ustawy z dnia 21 maja 2025 r. '
                       'o zmianie ustawy o ochronie praw nabywcy lokalu mieszkalnego lub domu jednorodzinnego '
                       'oraz Deweloperskim Funduszu Gwarancyjnym (Dz. U. 2025 poz. 758)')
    
    # Wydawca
    publisher = ET.SubElement(dataset_obj, 'dct:publisher')
    publisher_org = ET.SubElement(publisher, 'foaf:Organization')
    
    pub_name = ET.SubElement(publisher_org, 'foaf:name')
    pub_name.text = 'BRASPOL PAWEŁ WIĘCH'
    
    pub_homepage = ET.SubElement(publisher_org, 'foaf:homepage')
    pub_homepage.set('rdf:resource', 'https://www.braspol.pl')
    
    # Dane kontaktowe
    contact_point = ET.SubElement(dataset_obj, 'dcat:contactPoint')
    contact = ET.SubElement(contact_point, 'vcard:Organization')
    
    contact_fn = ET.SubElement(contact, 'vcard:fn')
    contact_fn.text = 'BRASPOL PAWEŁ WIĘCH'
    
    contact_email = ET.SubElement(contact, 'vcard:hasEmail')
    contact_email.set('rdf:resource', 'mailto:braspol@onet.pl')
    
    contact_tel = ET.SubElement(contact, 'vcard:hasTelephone')
    contact_tel.set('rdf:resource', 'tel:+48502930015')
    
    # Data wydania
    issued = ET.SubElement(dataset_obj, 'dct:issued')
    issued.set('rdf:datatype', 'http://www.w3.org/2001/XMLSchema#date')
    issued.text = '2025-02-09'
    
    # Data modyfikacji
    modified = ET.SubElement(dataset_obj, 'dct:modified')
    modified.set('rdf:datatype', 'http://www.w3.org/2001/XMLSchema#dateTime')
    modified.text = datetime.now().isoformat()
    
    # Słowa kluczowe
    for keyword in ['deweloper', 'nieruchomości', 'ceny mieszkań', 'rynek mieszkaniowy', 'Braspol', 'Zielonka']:
        kw = ET.SubElement(dataset_obj, 'dcat:keyword')
        kw.set('xml:lang', 'pl')
        kw.text = keyword
    
    # Język
    language = ET.SubElement(dataset_obj, 'dct:language')
    language.text = 'pl'
    
    # Częstotliwość aktualizacji
    frequency = ET.SubElement(dataset_obj, 'dct:accrualPeriodicity')
    frequency.set('rdf:resource', 'http://publications.europa.eu/resource/authority/frequency/DAILY')
    
    # Kategoria tematyczna
    theme = ET.SubElement(dataset_obj, 'dcat:theme')
    theme.set('rdf:resource', 'http://publications.europa.eu/resource/authority/data-theme/ECON')
    
    # Zakres czasowy
    temporal = ET.SubElement(dataset_obj, 'dct:temporal')
    period = ET.SubElement(temporal, 'dct:PeriodOfTime')
    start_date = ET.SubElement(period, 'dcat:startDate')
    start_date.set('rdf:datatype', 'http://www.w3.org/2001/XMLSchema#date')
    start_date.text = '2025-02-09'
    
    # Pokrycie przestrzenne
    spatial = ET.SubElement(dataset_obj, 'dct:spatial')
    location = ET.SubElement(spatial, 'dct:Location')
    loc_label = ET.SubElement(location, 'rdfs:label', {'xmlns:rdfs': 'http://www.w3.org/2000/01/rdf-schema#'})
    loc_label.text = 'Zielonka, Polska'
    
    # Licencja
    license_elem = ET.SubElement(dataset_obj, 'dct:license')
    license_elem.set('rdf:resource', 'https://creativecommons.org/publicdomain/zero/1.0/')
    
    # Dystrybucja CSV
    distribution_csv = ET.SubElement(dataset_obj, 'dcat:distribution')
    dist_csv_obj = ET.SubElement(distribution_csv, 'dcat:Distribution')
    dist_csv_obj.set('rdf:about', 'https://www.braspol.pl/api/data.csv')
    
    csv_title = ET.SubElement(dist_csv_obj, 'dct:title')
    csv_title.set('xml:lang', 'pl')
    csv_title.text = 'Ceny mieszkań - CSV'
    
    csv_access = ET.SubElement(dist_csv_obj, 'dcat:accessURL')
    csv_access.set('rdf:resource', 'https://www.braspol.pl/api/data.csv')
    
    csv_download = ET.SubElement(dist_csv_obj, 'dcat:downloadURL')
    csv_download.set('rdf:resource', 'https://www.braspol.pl/api/data.csv')
    
    csv_format = ET.SubElement(dist_csv_obj, 'dct:format')
    csv_format.text = 'CSV'
    
    csv_media = ET.SubElement(dist_csv_obj, 'dcat:mediaType')
    csv_media.text = 'text/csv'
    
    csv_issued = ET.SubElement(dist_csv_obj, 'dct:issued')
    csv_issued.set('rdf:datatype', 'http://www.w3.org/2001/XMLSchema#dateTime')
    csv_issued.text = datetime.now().isoformat()
    
    # Dystrybucja JSON-LD
    distribution_jsonld = ET.SubElement(dataset_obj, 'dcat:distribution')
    dist_jsonld_obj = ET.SubElement(distribution_jsonld, 'dcat:Distribution')
    dist_jsonld_obj.set('rdf:about', 'https://www.braspol.pl/api/data.jsonld')
    
    jsonld_title = ET.SubElement(dist_jsonld_obj, 'dct:title')
    jsonld_title.set('xml:lang', 'pl')
    jsonld_title.text = 'Ceny mieszkań - JSON-LD'
    
    jsonld_access = ET.SubElement(dist_jsonld_obj, 'dcat:accessURL')
    jsonld_access.set('rdf:resource', 'https://www.braspol.pl/api/data.jsonld')
    
    jsonld_download = ET.SubElement(dist_jsonld_obj, 'dcat:downloadURL')
    jsonld_download.set('rdf:resource', 'https://www.braspol.pl/api/data.jsonld')
    
    jsonld_format = ET.SubElement(dist_jsonld_obj, 'dct:format')
    jsonld_format.text = 'JSON-LD'
    
    jsonld_media = ET.SubElement(dist_jsonld_obj, 'dcat:mediaType')
    jsonld_media.text = 'application/ld+json'
    
    jsonld_issued = ET.SubElement(dist_jsonld_obj, 'dct:issued')
    jsonld_issued.set('rdf:datatype', 'http://www.w3.org/2001/XMLSchema#dateTime')
    jsonld_issued.text = datetime.now().isoformat()
    
    # Formatowanie XML
    xml_str = minidom.parseString(ET.tostring(root, encoding='utf-8')).toprettyxml(indent="  ", encoding="utf-8")
    
    return xml_str


def _build_flattened_records(dane_dewelopera, oferty, max_pom, max_rab, max_swi):
    """Buduje spłaszczone rekordy dla CSV i XLSX"""
    for oferta in oferty:
        ceny_list = list(oferta.ceny.all())
        ostatnia_cena = ceny_list[-1] if ceny_list else None
        cena_m2 = (
            round(float(ostatnia_cena.kwota) / float(oferta.metraz), 2)
            if ostatnia_cena and oferta.metraz else ""
        )
        
        # Suma pomieszczeń przynależnych
        suma_pomieszczen = sum(
            float(p.cena) for p in oferta.pomieszczenia_przynalezne.all() if p.cena
        )
        
        # Suma innych świadczeń
        suma_swiadczen = sum(
            float(s.kwota) for s in oferta.inne_swiadczenia.all() if s.kwota
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
            "id_przedsiewziecia": oferta.inwestycja.unikalny_identyfikator_przedsiewziecia if oferta.inwestycja else "",
            "nazwa_przedsiewziecia": oferta.inwestycja.nazwa if oferta.inwestycja else "",
            "adres_przedsiewziecia": oferta.inwestycja.adres if oferta.inwestycja else "",
            "numer_lokalu": oferta.numer_lokalu or "",
            "numer_oferty": oferta.numer_oferty if hasattr(oferta, 'numer_oferty') else "",
            "rodzaj_lokalu": oferta.rodzaj_lokalu.nazwa if oferta.rodzaj_lokalu else "mieszkanie",
            "powierzchnia_uzytkowa_m2": float(oferta.metraz) if oferta.metraz else "",
            "liczba_pokoi": oferta.pokoje,
            "cena_lokalu_brutto_pln": float(ostatnia_cena.kwota) if ostatnia_cena else "",
            "cena_za_m2_brutto_pln": cena_m2,
            "cena_pomieszczen_przynaleznych_pln": suma_pomieszczen if suma_pomieszczen > 0 else "",
            "inne_swiadczenia_pieniezne_pln": suma_swiadczen if suma_swiadczen > 0 else "",
            "data_aktualizacji": ostatnia_cena.data.isoformat() if ostatnia_cena else date.today().isoformat(),
        }

        # Dodaj szczegóły pomieszczeń
        for i, p in enumerate(oferta.pomieszczenia_przynalezne.all()):
            rekord_csv[f"pomieszczenie_{i+1}_nazwa"] = p.nazwa
            rekord_csv[f"pomieszczenie_{i+1}_powierzchnia_m2"] = float(p.powierzchnia) if p.powierzchnia else ""
            rekord_csv[f"pomieszczenie_{i+1}_cena_pln"] = float(p.cena) if p.cena else ""
        
        # Dodaj rabaty
        for i, r in enumerate(oferta.rabaty.all()):
            rekord_csv[f"rabat_{i+1}_nazwa"] = r.nazwa
            rekord_csv[f"rabat_{i+1}_wartosc"] = float(r.wartosc) if r.wartosc else ""
            rekord_csv[f"rabat_{i+1}_typ"] = r.typ
        
        # Dodaj inne świadczenia
        for i, s in enumerate(oferta.inne_swiadczenia.all()):
            rekord_csv[f"swiadczenie_{i+1}_nazwa"] = s.nazwa
            rekord_csv[f"swiadczenie_{i+1}_kwota_pln"] = float(s.kwota) if s.kwota else ""

        yield rekord_csv


def generate_csv_data():
    """Generuje dane CSV zgodnie z wymogami ustawy"""
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
        "id_przedsiewziecia", "nazwa_przedsiewziecia", "adres_przedsiewziecia",
        "numer_lokalu", "numer_oferty", "rodzaj_lokalu",
        "powierzchnia_uzytkowa_m2", "liczba_pokoi",
        "cena_lokalu_brutto_pln", "cena_za_m2_brutto_pln",
        "cena_pomieszczen_przynaleznych_pln", "inne_swiadczenia_pieniezne_pln",
        "data_aktualizacji",
    ]
    
    for i in range(max_pom):
        fieldnames.extend([
            f"pomieszczenie_{i+1}_nazwa",
            f"pomieszczenie_{i+1}_powierzchnia_m2",
            f"pomieszczenie_{i+1}_cena_pln"
        ])
    
    for i in range(max_rab):
        fieldnames.extend([
            f"rabat_{i+1}_nazwa",
            f"rabat_{i+1}_wartosc",
            f"rabat_{i+1}_typ"
        ])
    
    for i in range(max_swi):
        fieldnames.extend([
            f"swiadczenie_{i+1}_nazwa",
            f"swiadczenie_{i+1}_kwota_pln"
        ])

    csv_output = io.BytesIO()
    csv_output.write(b'\xEF\xBB\xBF')  # UTF-8 BOM
    
    writer = csv.writer(io.TextIOWrapper(csv_output, encoding='utf-8-sig'), delimiter=';')
    writer.writerow(fieldnames)

    for rekord in _build_flattened_records(dane_dewelopera, oferty, max_pom, max_rab, max_swi):
        row = [rekord.get(field, "") for field in fieldnames]
        writer.writerow(row)

    csv_content = csv_output.getvalue()
    csv_output.close()
    
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
        "id_przedsiewziecia", "nazwa_przedsiewziecia", "adres_przedsiewziecia",
        "numer_lokalu", "numer_oferty", "rodzaj_lokalu",
        "powierzchnia_uzytkowa_m2", "liczba_pokoi",
        "cena_lokalu_brutto_pln", "cena_za_m2_brutto_pln",
        "cena_pomieszczen_przynaleznych_pln", "inne_swiadczenia_pieniezne_pln",
        "data_aktualizacji",
    ]
    
    for i in range(max_pom):
        fieldnames.extend([
            f"pomieszczenie_{i+1}_nazwa",
            f"pomieszczenie_{i+1}_powierzchnia_m2",
            f"pomieszczenie_{i+1}_cena_pln"
        ])
    
    for i in range(max_rab):
        fieldnames.extend([
            f"rabat_{i+1}_nazwa",
            f"rabat_{i+1}_wartosc",
            f"rabat_{i+1}_typ"
        ])
    
    for i in range(max_swi):
        fieldnames.extend([
            f"swiadczenie_{i+1}_nazwa",
            f"swiadczenie_{i+1}_kwota_pln"
        ])

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
    """Generuje dane JSON-LD zgodnie z schema.org"""
    dane_dewelopera = get_deweloper_data()
    oferty = get_oferty_data()
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    if not oferty.exists():
        return {"@type": "Dataset", "name": "Brak ofert", "dateModified": current_date}
    
    jsonld_context = {
        "@vocab": "http://schema.org/",
        "nip": "http://schema.org/vatID",
        "regon": "http://schema.org/taxID",
    }

    offers = []
    
    for oferta in oferty:
        ceny_list = list(oferta.ceny.all())
        ostatnia_cena = ceny_list[-1] if ceny_list else None
        cena_m2 = (
            round(float(ostatnia_cena.kwota) / float(oferta.metraz), 2)
            if ostatnia_cena and oferta.metraz else None
        )

        pomieszczenia_przynalezne = [
            {
                "nazwa": p.nazwa,
                "powierzchnia_m2": float(p.powierzchnia) if p.powierzchnia else None,
                "cena_pln": float(p.cena) if p.cena else None
            }
            for p in oferta.pomieszczenia_przynalezne.all()
        ]
        
        rabaty = [
            {
                "nazwa": r.nazwa,
                "wartosc": float(r.wartosc) if r.wartosc else None,
                "typ": r.typ
            }
            for r in oferta.rabaty.all()
        ]
        
        inne_swiadczenia = [
            {
                "nazwa": s.nazwa,
                "kwota_pln": float(s.kwota) if s.kwota else None
            }
            for s in oferta.inne_swiadczenia.all()
        ]

        offer = {
            "@type": "Product",
            "name": f"Mieszkanie {oferta.numer_lokalu or oferta.id}",
            "description": f"Mieszkanie {oferta.pokoje}-pokojowe o powierzchni {oferta.metraz} m²",
            "category": "Nieruchomości/Mieszkania",
            "offers": {
                "@type": "Offer",
                "priceCurrency": "PLN",
                "price": float(ostatnia_cena.kwota) if ostatnia_cena else None,
                "priceValidUntil": ostatnia_cena.data.isoformat() if ostatnia_cena else None,
                "availability": "https://schema.org/InStock",
                "seller": {
                    "@type": "Organization",
                    "name": dane_dewelopera["nazwa_firmy"],
                    "vatID": dane_dewelopera["nip"]
                }
            },
            "additionalProperty": [
                {
                    "@type": "PropertyValue",
                    "name": "Powierzchnia użytkowa",
                    "value": float(oferta.metraz) if oferta.metraz else None,
                    "unitText": "m²"
                },
                {
                    "@type": "PropertyValue",
                    "name": "Liczba pokoi",
                    "value": oferta.pokoje
                },
                {
                    "@type": "PropertyValue",
                    "name": "Cena za m²",
                    "value": cena_m2,
                    "unitText": "PLN/m²"
                }
            ],
            "itemOffered": {
                "@type": "Apartment",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": oferta.inwestycja.adres if oferta.inwestycja else "",
                    "addressLocality": dane_dewelopera["miejscowosc"],
                    "addressRegion": dane_dewelopera["wojewodztwo"],
                    "postalCode": dane_dewelopera["kod_pocztowy"],
                    "addressCountry": dane_dewelopera["kraj"]
                },
                "numberOfRooms": oferta.pokoje,
                "floorSize": {
                    "@type": "QuantitativeValue",
                    "value": float(oferta.metraz) if oferta.metraz else None,
                    "unitCode": "MTK"
                }
            },
            "pomieszczenia_przynalezne": pomieszczenia_przynalezne,
            "rabaty": rabaty,
            "inne_swiadczenia_pieniezne": inne_swiadczenia,
        }
        offers.append(offer)

    jsonld_data = {
        "@context": jsonld_context,
        "@type": "Dataset",
        "name": "Ceny ofertowe mieszkań dewelopera BRASPOL Paweł Więch",
        "description": "Zestaw danych zgodny z art. 19a i 19b ustawy o ochronie praw nabywcy lokalu mieszkalnego",
        "dateModified": current_date,
        "license": "https://creativecommons.org/publicdomain/zero/1.0/",
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
        "distribution": [
            {
                "@type": "DataDownload",
                "encodingFormat": "text/csv",
                "contentUrl": "https://www.braspol.pl/api/data.csv"
            },
            {
                "@type": "DataDownload",
                "encodingFormat": "application/ld+json",
                "contentUrl": "https://www.braspol.pl/api/data.jsonld"
            }
        ],
        "itemListElement": offers
    }
    
    return jsonld_data


def send_to_dane_gov_pl(csv_url, metadata_url):
    """
    Wysyła powiadomienie na portal dane.gov.pl (opcjonalne)
    
    UWAGA: To jest przykładowa funkcja - rzeczywiste API może wymagać innych parametrów.
    Skontaktuj się z administratorami portalu dane.gov.pl aby uzyskać szczegóły API.
    """
    api_endpoint = getattr(settings, 'DANE_GOV_PL_API_ENDPOINT', None)
    api_key = getattr(settings, 'DANE_GOV_PL_API_KEY', None)
    
    if not api_endpoint or not api_key:
        return False, "Brak konfiguracji API dla dane.gov.pl"
    
    try:
        payload = {
            "organization": "BRASPOL PAWEŁ WIĘCH",
            "nip": "1250994717",
            "dataset_title": "Ceny ofertowe mieszkań",
            "dataset_url": metadata_url,
            "data_url": csv_url,
            "format": "CSV",
            "update_frequency": "daily",
            "category": "real_estate"
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(api_endpoint, json=payload, headers=headers, timeout=30)
        
        if response.status_code in [200, 201]:
            return True, "Dane wysłane pomyślnie"
        else:
            return False, f"Błąd HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, f"Błąd podczas wysyłki: {str(e)}"


class Command(BaseCommand):
    help = "Automatyczne generowanie i publikacja raportów zgodnie z ustawą"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("\n" + "="*70))
        self.stdout.write(self.style.WARNING("RAPORT DZIENNY - BRASPOL"))
        self.stdout.write(self.style.WARNING("Zgodność z art. 19a i 19b ustawy"))
        self.stdout.write(self.style.WARNING("="*70 + "\n"))

        dane_dewelopera = get_deweloper_data()
        oferty = get_oferty_data()

        if not oferty.exists():
            self.stdout.write(self.style.WARNING("⚠️  Nie znaleziono dostępnych ofert do raportu."))
            return

        self.stdout.write(self.style.SUCCESS(f"✅ Znaleziono {oferty.count()} dostępnych ofert"))

        # Katalog raportów
        raporty_dir = "raporty"
        if not os.path.exists(raporty_dir):
            os.makedirs(raporty_dir)

        # Katalog dla API (statyczny)
        api_dir = os.path.join("oferty", "templates", "api")
        if not os.path.exists(api_dir):
            os.makedirs(api_dir)

        data_raportu = str(date.today())
        
        # 1. Generuj CSV
        self.stdout.write("\n📄 Generowanie CSV...")
        csv_content = generate_csv_data()
        csv_path = f"{raporty_dir}/Raport_ofert_Braspol_{data_raportu}.csv"
        with open(csv_path, "w", encoding="utf-8-sig") as f:
            f.write(csv_content)
        self.stdout.write(self.style.SUCCESS(f"   ✅ Zapisano: {csv_path}"))
        
        # 2. Generuj MD5 dla CSV
        csv_md5 = calculate_md5(csv_content)
        csv_md5_path = f"{csv_path}.md5"
        with open(csv_md5_path, "w") as f:
            f.write(csv_md5)
        self.stdout.write(self.style.SUCCESS(f"   ✅ MD5: {csv_md5}"))
        
        # 3. Generuj XLSX
        self.stdout.write("\n📊 Generowanie XLSX...")
        xlsx_content = generate_xlsx_data()
        xlsx_path = f"{raporty_dir}/Raport_ofert_Braspol_{data_raportu}.xlsx"
        with open(xlsx_path, "wb") as f:
            f.write(xlsx_content)
        self.stdout.write(self.style.SUCCESS(f"   ✅ Zapisano: {xlsx_path}"))
        
        # 4. Generuj MD5 dla XLSX
        xlsx_md5 = calculate_md5(xlsx_content, is_binary=True)
        xlsx_md5_path = f"{xlsx_path}.md5"
        with open(xlsx_md5_path, "w") as f:
            f.write(xlsx_md5)
        self.stdout.write(self.style.SUCCESS(f"   ✅ MD5: {xlsx_md5}"))
        
        # 5. Generuj JSON-LD
        self.stdout.write("\n🔗 Generowanie JSON-LD...")
        jsonld_content = generate_jsonld_data()
        jsonld_path = f"{raporty_dir}/raport_{data_raportu}.jsonld"
        with open(jsonld_path, "w", encoding="utf-8") as f:
            json.dump(jsonld_content, f, ensure_ascii=False, indent=2)
        self.stdout.write(self.style.SUCCESS(f"   ✅ Zapisano: {jsonld_path}"))
        
        # 6. Generuj MD5 dla JSON-LD
        jsonld_str = json.dumps(jsonld_content, ensure_ascii=False)
        jsonld_md5 = calculate_md5(jsonld_str)
        jsonld_md5_path = f"{jsonld_path}.md5"
        with open(jsonld_md5_path, "w") as f:
            f.write(jsonld_md5)
        self.stdout.write(self.style.SUCCESS(f"   ✅ MD5: {jsonld_md5}"))
        
        # 7. Generuj metadata.xml
        self.stdout.write("\n📋 Generowanie metadata.xml...")
        metadata_content = generate_metadata_xml()
        metadata_path = os.path.join(api_dir, "metadata.xml")
        with open(metadata_path, "wb") as f:
            f.write(metadata_content)
        self.stdout.write(self.style.SUCCESS(f"   ✅ Zapisano: {metadata_path}"))
        
        # 8. Generuj MD5 dla metadata.xml
        metadata_md5 = calculate_md5(metadata_content, is_binary=True)
        metadata_md5_path = f"{metadata_path}.md5"
        with open(metadata_md5_path, "w") as f:
            f.write(metadata_md5)
        self.stdout.write(self.style.SUCCESS(f"   ✅ MD5: {metadata_md5}"))
        
        # 9. Opcjonalnie: wyślij powiadomienie na dane.gov.pl
        self.stdout.write("\n🌐 Sprawdzanie możliwości wysyłki na dane.gov.pl...")
        success, message = send_to_dane_gov_pl(
            "https://www.braspol.pl/api/data.csv",
            "https://www.braspol.pl/api/metadata.xml"
        )
        
        if success:
            self.stdout.write(self.style.SUCCESS(f"   ✅ {message}"))
        else:
            self.stdout.write(self.style.WARNING(f"   ⚠️  {message}"))
            self.stdout.write(self.style.WARNING("   ℹ️  Dane są dostępne publicznie pod adresami:"))
            self.stdout.write(self.style.WARNING("      • https://www.braspol.pl/api/data.csv"))
            self.stdout.write(self.style.WARNING("      • https://www.braspol.pl/api/metadata.xml"))

        self.stdout.write(self.style.SUCCESS("\n" + "="*70))
        self.stdout.write(self.style.SUCCESS("✅ RAPORT ZAKOŃCZONY POMYŚLNIE"))
        self.stdout.write(self.style.SUCCESS("="*70 + "\n"))
