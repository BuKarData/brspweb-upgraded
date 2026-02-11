from django.http import HttpResponse
import json 
import hashlib
from datetime import datetime
from oferty.management.commands.raportuj_auto import (
    generate_jsonld_data,
    generate_csv_data,
    generate_xlsx_data,
    generate_metadata_xml,
)
from django.http import FileResponse
import os
from django.conf import settings

def calculate_md5(content, is_binary=False):
    """Oblicza sumę kontrolną MD5"""
    md5_hash = hashlib.md5()
    if is_binary:
        md5_hash.update(content)
    else:
        md5_hash.update(content.encode('utf-8'))
    return md5_hash.hexdigest()

def metadata_xml(request):
    """Serwuje metadata.xml zgodny z dane.gov.pl (urn:otwarte-dane:harvester:1.13)"""
    xml_file_path = os.path.join(settings.BASE_DIR, 'oferty', 'templates', 'api', 'metadata.xml')

    if os.path.exists(xml_file_path):
        return FileResponse(open(xml_file_path, 'rb'), content_type='application/xml')

    # Fallback: generuj dynamicznie jesli plik nie istnieje
    content = generate_metadata_xml()
    return HttpResponse(content, content_type='application/xml')

def metadata_xml_md5(request):
    """Serwuje MD5 dla metadata.xml"""
    xml_file_path = os.path.join(settings.BASE_DIR, 'oferty', 'templates', 'api', 'metadata.xml')

    if os.path.exists(xml_file_path):
        with open(xml_file_path, 'rb') as f:
            content = f.read()
    else:
        content = generate_metadata_xml()

    md5_hash = calculate_md5(content, is_binary=True)
    response = HttpResponse(md5_hash, content_type='text/plain')
    response['Content-Disposition'] = 'inline; filename="metadata.xml.md5"'
    return response

def data_api_view(request):
    """Serwuje dane w różnych formatach (CSV, JSON-LD, XLSX)"""
    try:
        if request.path.endswith('.jsonld'):
            data = generate_jsonld_data()
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            response = HttpResponse(json_data, content_type='application/ld+json; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename="data.jsonld"'
            
        elif request.path.endswith('.csv'):
            data = generate_csv_data()
            # UTF-8 BOM (\ufeff) na poczatku dla kompatybilnosci z Excel
            response = HttpResponse(
                '\ufeff' + data,
                content_type='text/csv; charset=utf-8-sig'
            )
            response['Content-Disposition'] = 'attachment; filename="data.csv"'
            
        elif request.path.endswith('.xlsx'):
            data = generate_xlsx_data()
            response = HttpResponse(
                data,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="data.xlsx"'
            
        else:
            return HttpResponse('Format not supported', status=400, content_type='text/plain')
        
        response['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        return response
        
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500, content_type='text/plain')


def data_api_md5_view(request):
    """Serwuje MD5 dla danych API"""
    try:
        if request.path.endswith('.csv.md5'):
            data = generate_csv_data()
            md5_hash = calculate_md5(data)
            response = HttpResponse(md5_hash, content_type='text/plain')
            response['Content-Disposition'] = 'inline; filename="data.csv.md5"'
            
        elif request.path.endswith('.jsonld.md5'):
            data = generate_jsonld_data()
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            md5_hash = calculate_md5(json_data)
            response = HttpResponse(md5_hash, content_type='text/plain')
            response['Content-Disposition'] = 'inline; filename="data.jsonld.md5"'
            
        elif request.path.endswith('.xlsx.md5'):
            data = generate_xlsx_data()
            md5_hash = calculate_md5(data, is_binary=True)
            response = HttpResponse(md5_hash, content_type='text/plain')
            response['Content-Disposition'] = 'inline; filename="data.xlsx.md5"'
            
        else:
            return HttpResponse('Format not supported', status=400, content_type='text/plain')
        
        return response
        
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500, content_type='text/plain')