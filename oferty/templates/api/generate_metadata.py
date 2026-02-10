import os
import hashlib
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


# --- Ścieżki ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder oferty/templates/api
# Poprawiona ścieżka - cofamy się trzy poziomy do braspol/, potem do raporty/
REPORTS_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', '..', 'raporty'))
TEMPLATE_DIR = os.path.join(BASE_DIR)  # metadata_template.xml w tym samym folderze
OUTPUT_XML = os.path.join(BASE_DIR, 'metadata.xml')  # zapis w oferty/templates/api/

# --- Funkcja do MD5 ---
def md5sum(filepath):
    if not os.path.exists(filepath):
        print(f"⚠️ Plik nie istnieje: {filepath}")
        return ""
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

# --- Lista raportów ze stałymi nazwami ---
files = {
    "jsonld": "data.jsonld",
    "csv": "data.csv", 
    "xlsx": "data.xlsx"
}

# --- Dane dla Jinja ---
current_date = datetime.now().strftime("%Y-%m-%d")
current_date_nodash = datetime.now().strftime("%Y%m%d")

reports = [
    {
        "id": "braspol-jsonld",
        "title": "Ceny nieruchomości - JSON-LD",
        "description": "Dane w formacie JSON-LD zgodnym ze schema.org",
        "format": "application/ld+json",
        "url": f"https://www.braspol.pl/api/{files['jsonld']}", 
        "md5": md5sum(os.path.join(REPORTS_DIR, "raport_2025-09-14.jsonld")),  # ale MD5 z aktualnego pliku
        "availability": "remote"
    },
    {
        "id": "braspol-csv",
        "title": "Ceny nieruchomości - CSV",
        "description": "Dane w formacie CSV",
        "format": "text/csv",
        "url": f"https://www.braspol.pl/api/{files['csv']}",
        "md5": md5sum(os.path.join(REPORTS_DIR, "Raport ofert firmy Braspol_2025-09-14.csv")),
        "availability": "remote"
    },
    {
        "id": "braspol-xlsx",
        "title": "Ceny nieruchomości - Excel XLSX",
        "description": "Dane w formacie Excel XLSX",
        "format": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "url": f"https://www.braspol.pl/api/{files['xlsx']}",
        "md5": md5sum(os.path.join(REPORTS_DIR, "Raport ofert firmy Braspol_2025-09-14.xlsx")),
        "availability": "remote"
    }
]

# --- Renderowanie Jinja ---
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
template = env.get_template('metadata_template.xml')
xml_content = template.render(
    current_date=current_date,
    current_date_nodash=current_date_nodash,
    reports=reports
)

# --- Zapis XML ---
with open(OUTPUT_XML, "w", encoding="utf-8") as f:
    f.write(xml_content)

print(f"✅ Plik metadata.xml został zapisany w {OUTPUT_XML}")