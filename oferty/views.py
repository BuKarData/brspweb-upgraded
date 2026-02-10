from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.db.models import Prefetch
from .forms import OfertaForm, CenaForm
from .models import Oferta, Cena, Inwestycja
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
from datetime import datetime
from django.conf import settings

class OfertyAPIView(APIView):
    """
    API zwracające listę ofert w formacie JSON gotowym dla gov.dane.pl
    """
    def get(self, request):
        ceny_prefetch = Prefetch('ceny', queryset=Cena.objects.order_by('data'))
        oferty = Oferta.objects.prefetch_related(
            'inwestycja', 'pomieszczenia_przynalezne', 'rabaty', 'inne_swiadczenia', ceny_prefetch
        ).all()

        dane_dewelopera = {
            "nip": "1250994717",
            "regon": "141371661",
            "nazwa_firmy": "BRASPOL PAWEŁ WIĘCH",
            "adres_biura": "ul. Kilińskiego 92A 05-220 ZIELONKA"
        }

        wynik = []

        for oferta in oferty:
            ceny_list = list(oferta.ceny.all())
            ostatnia_cena = ceny_list[-1] if ceny_list else None
            cena_m2 = round(float(ostatnia_cena.kwota)/float(oferta.metraz), 2) if ostatnia_cena and oferta.metraz else None

            rekord = {
                "deweloper": dane_dewelopera,
                "inwestycja": {
                    "unikalny_identyfikator": getattr(oferta.inwestycja, 'unikalny_identyfikator_przedsiewziecia', None),
                    "adres": getattr(oferta.inwestycja, 'adres', None),
                    "numer_pozwolenia_na_budowe": getattr(oferta.inwestycja, 'numer_pozwolenia', None)
                },
                "oferta": {
                    "id": oferta.id,
                    "numer_lokalu": oferta.numer_lokalu,
                    "rodzaj_lokalu": getattr(oferta.rodzaj_lokalu, 'nazwa', None),
                    "metraz": float(oferta.metraz) if oferta.metraz else None,
                    "pokoje": oferta.pokoje,
                    "status": oferta.status,
                    "cena": float(ostatnia_cena.kwota) if ostatnia_cena else None,
                    "cena_za_m2": cena_m2,
                    "data_ceny": ostatnia_cena.data.isoformat() if ostatnia_cena else None
                },
                "dodatkowe_oplaty": {
                    "pomieszczenia_przynaleznie": [{"nazwa": p.nazwa, "cena": float(p.cena)} for p in oferta.pomieszczenia_przynalezne.all()],
                    "rabaty_i_promocje": [{"nazwa": r.nazwa, "wartosc": float(r.wartosc), "typ": r.typ, "data_od": r.data_od.isoformat(), "data_do": r.data_do.isoformat()} for r in oferta.rabaty.all()],
                    "inne_swiadczenia": [{"nazwa": s.nazwa, "kwota": float(s.kwota)} for s in oferta.inne_swiadczenia.all()]
                }
            }

            wynik.append(rekord)

        return Response(wynik, status=status.HTTP_200_OK)


def home(request):
    # Prefetch dla cen i rzutów w ofertach
    ceny_prefetch = Prefetch('ceny', queryset=Cena.objects.order_by('data'))
    rzuty_prefetch = Prefetch('rzuty')
    
    # Pobieramy inwestycje z ofertami, które już mają prefetch dla cen i rzutów
    inwestycje = Inwestycja.objects.prefetch_related(
        Prefetch(
            'oferty', 
            queryset=Oferta.objects.prefetch_related(ceny_prefetch, rzuty_prefetch)
        )
    ).order_by('-data_dodania')

    # Dodajemy do każdej oferty ostatnią cenę i cenę za m²
    for inwestycja in inwestycje:
        for oferta in inwestycja.oferty.all():
            ceny = list(oferta.ceny.all())
            if ceny:
                ostatnia = ceny[-1]
                oferta.ostatnia_cena = ostatnia.kwota
                oferta.cena_m2 = float(oferta.ostatnia_cena) / float(oferta.metraz) if oferta.metraz else None
            else:
                oferta.ostatnia_cena = None
                oferta.cena_m2 = None

    return render(request, "home.html", {"inwestycje": inwestycje})


def lista_ofert(request):
    ceny_prefetch = Prefetch('ceny', queryset=Cena.objects.order_by('data'))
    oferty = Oferta.objects.all().prefetch_related(ceny_prefetch).order_by('-data_dodania')

    for oferta in oferty:
        ceny = list(oferta.ceny.all())
        oferta.ceny_list = []  # lista dla historii cen

        for c in ceny:
            try:
                kwota = float(c.kwota)
                oferta.ceny_list.append({'kwota': kwota, 'data': c.data})
            except (ValueError, TypeError):
                continue

        if oferta.ceny_list:
            ostatnia = oferta.ceny_list[-1]
            oferta.ostatnia_cena = ostatnia
            oferta.cena_m2 = int(ostatnia['kwota'] / float(oferta.metraz)) if oferta.metraz else None
        else:
            oferta.ostatnia_cena = None
            oferta.cena_m2 = None

        oferta.chart_data = {
            "labels": [str(c['data']) for c in oferta.ceny_list],
            "data": [c['kwota'] for c in oferta.ceny_list],
        }
        
    

    return render(request, "oferty/lista_ofert.html", {"oferty": oferty})

def szczegoly_inwestycji(request, pk):
    inwestycja = get_object_or_404(Inwestycja, pk=pk)
    oferty = inwestycja.oferty.all()  # używamy related_name="oferty"
    return render(request, "oferty/szczegoly_inwestycji.html", {
        "inwestycja": inwestycja,
        "oferty": oferty,
    })



# Dodawanie oferty
def dodaj_oferte(request):
    if request.method == "POST":
        form = OfertaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_ofert')
    else:
        form = OfertaForm()
    return render(request, "oferty/dodaj_oferte.html", {"form": form})


# Dodawanie ceny
def dodaj_cene(request, oferta_id):
    oferta = get_object_or_404(Oferta, id=oferta_id)
    if request.method == "POST":
        form = CenaForm(request.POST)
        if form.is_valid():
            cena = form.save(commit=False)
            cena.oferta = oferta
            cena.save()
            return redirect('lista_ofert')
    else:
        form = CenaForm()
    return render(request, "oferty/dodaj_cene.html", {"form": form, "oferta": oferta})


# AJAX dodawanie ceny
@csrf_exempt
def ajax_dodaj_cene(request, oferta_id):
    if request.method == "POST":
        oferta = get_object_or_404(Oferta, id=oferta_id)
        kwota = safe_float(request.POST.get("kwota"))
        data = request.POST.get("data")
        if kwota is not None and data:
            Cena.objects.create(oferta=oferta, kwota=kwota, data=data)
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "fail"}, status=400)


# --- Pomocnicza funkcja do bezpiecznej konwersji kwoty ---
def safe_float(value):
    """
    Konwertuje wartość na float, usuwa spacje i przecinki.
    Zwraca None jeśli konwersja się nie powiedzie.
    """
    if value is None:
        return None
    try:
        return float(str(value).replace(" ", "").replace(",", ""))
    except (ValueError, TypeError):
        return None


def system_status(request):
    """
    Endpoint statusu systemu - zwraca informacje o dostępności plików
    i ostatnich aktualizacjach
    """
    csv_path = os.path.join('oferty', 'templates', 'api', 'data.csv')
    metadata_path = os.path.join('oferty', 'templates', 'api', 'metadata.xml')
    
    status_data = {
        "status": "online",
        "csv_available": os.path.exists(csv_path),
        "metadata_available": os.path.exists(metadata_path),
        "last_csv_update": None,
        "last_metadata_update": None,
        "total_offers": Oferta.objects.filter(status="dostępne").count()
    }
    
    if os.path.exists(metadata_path):
        status_data["last_metadata_update"] = datetime.fromtimestamp(
            os.path.getmtime(metadata_path)
        ).isoformat()
    
    return JsonResponse(status_data)


@csrf_exempt
def manual_update(request):
    """
    Endpoint do ręcznego uruchomienia aktualizacji raportów
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        from django.core.management import call_command
        call_command('raportuj_auto')
        return JsonResponse({
            "status": "success",
            "message": "Raporty zostały zaktualizowane pomyślnie",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)