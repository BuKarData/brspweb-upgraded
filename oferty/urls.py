from django.contrib import admin
from django.urls import path, include
from oferty import views
from django.conf import settings
from django.conf.urls.static import static
from .views import home, lista_ofert, system_status, manual_update
from .api import data_api_view, data_api_md5_view, metadata_xml, metadata_xml_md5

urlpatterns = [
    path('', home, name='home'),
    path('oferty/', lista_ofert, name='lista_ofert'),
    path('system-status/', system_status, name='system_status'),
    path('api/manual-update/', manual_update, name='manual_update'),
    
    # API endpointy zgodne z ustawą
    path('api/data.csv', data_api_view, name='data-csv'),
    path('api/data.csv.md5', data_api_md5_view, name='data-csv-md5'),
    path('api/data.jsonld', data_api_view, name='data-jsonld'),
    path('api/data.jsonld.md5', data_api_md5_view, name='data-jsonld-md5'),
    path('api/data.xlsx', data_api_view, name='data-xlsx'),
    path('api/data.xlsx.md5', data_api_md5_view, name='data-xlsx-md5'),
    path('api/metadata.xml', metadata_xml, name='metadata-xml'),
    path('api/metadata.xml.md5', metadata_xml_md5, name='metadata-xml-md5'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)