from django.contrib import admin
from .models import (
    Oferta,
    Cena,
    Inwestycja,
    InwestycjaZdjecie,
    RodzajLokalu,
    PomieszczeniePrzynalezne,
    SwiadczeniePieniezne,
    Rabat,
    Rzut,
)

@admin.register(RodzajLokalu)
class RodzajLokaluAdmin(admin.ModelAdmin):
    list_display = ("nazwa",)
    search_fields = ("nazwa",)


class PomieszczeniePrzynalezneInline(admin.TabularInline):
    model = PomieszczeniePrzynalezne
    extra = 1

class SwiadczeniePieniezneInline(admin.TabularInline):
    model = SwiadczeniePieniezne
    extra = 1

class RabatInline(admin.TabularInline):
    model = Rabat
    extra = 1


class InwestycjaZdjecieInline(admin.TabularInline):
    model = InwestycjaZdjecie
    extra = 1

    def inwestycja_nazwa(self, obj):
        return obj.inwestycja.nazwa if obj.inwestycja else "Brak inwestycji"

class RzutInline(admin.TabularInline): 
    model = Rzut
    extra = 1  

@admin.register(Inwestycja)
class InwestycjaAdmin(admin.ModelAdmin):
      inlines = [InwestycjaZdjecieInline]
      list_display = (
        "nazwa",
        "adres",
        "data_dodania",
        "unikalny_identyfikator_przedsiewziecia",
        "numer_pozwolenia"
    )
      search_fields = ("nazwa", "adres")
    # Dodanie nowych pól do formularza inwestycji
      fields = (
        "nazwa",
        "adres",
        "opis",
        "standard",
        "zdjecie",
        "unikalny_identyfikator_przedsiewziecia",
        "numer_pozwolenia",
        "termin_rozpoczecia",
        "termin_zakonczenia"
    )


@admin.register(InwestycjaZdjecie)
class InwestycjaZdjecieAdmin(admin.ModelAdmin):
    list_display = ('obraz', 'inwestycja_nazwa')

    def inwestycja_nazwa(self, obj):
        return obj.inwestycja.nazwa if obj.inwestycja else "Brak inwestycji"
    
    inwestycja_nazwa.short_description = "Inwestycja"


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    inlines = [
        PomieszczeniePrzynalezneInline,
        SwiadczeniePieniezneInline,
        RabatInline,
        RzutInline,
    ]
    list_display = (
        "numer_lokalu",
        "numer_oferty",
        "metraz",
        "pokoje",
        "status",
        "rodzaj_lokalu",
        "data_dodania"

    )
    list_filter = ("status", "rodzaj_lokalu")
    search_fields = ("numer_lokalu", "numer_oferty")
    # Zmieniamy pola w formularzu, aby umożliwić edycję wszystkich atrybutów
    fieldsets = (
        ("Informacje podstawowe", {
            "fields": (
                "inwestycja",
                "numer_lokalu",
                "numer_oferty",
                "rodzaj_lokalu",
                "metraz",
                "pokoje",
                "status",
                "zdjecie"
            )
        }),
        ("Szczegóły", {
            "fields": ("adres",)
        }),
    )
class RzutAdmin(admin.ModelAdmin):
    list_display = ("id", "oferta", "zdjecie")

@admin.register(Cena)
class CenaAdmin(admin.ModelAdmin):
    list_display = ("oferta", "kwota", "data")
    list_filter = ("data",)