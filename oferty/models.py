from django.db import models
from decimal import Decimal

class Inwestycja(models.Model):
    nazwa = models.CharField(max_length=200)
    adres = models.CharField(max_length=300)
    data_dodania = models.DateTimeField(auto_now_add=True)
    zdjecie = models.ImageField(upload_to="inwestycje/", blank=True, null=True)
    opis = models.TextField(blank=True, null=True)
    standard = models.TextField(blank=True, null=True)
    unikalny_identyfikator_przedsiewziecia = models.CharField(max_length=200, unique=True, null=True, blank=True, verbose_name="Unikalny identyfikator przedsięwzięcia")
    numer_pozwolenia = models.CharField(max_length=200, null=True, blank=True, verbose_name="Numer pozwolenia na budowę")
    termin_rozpoczecia = models.DateField(null=True, blank=True, verbose_name="Termin rozpoczęcia inwestycji")
    termin_zakonczenia = models.DateField(null=True, blank=True, verbose_name="Termin zakończenia inwestycji")

    def __str__(self):
        return self.nazwa


class Oferta(models.Model):
    STATUS_CHOICES = [
        ("dostępne", "Dostępne"),
        ("sprzedane", "Sprzedane"),
        ("rezerwacja", "Rezerwacja"),
    ]

    inwestycja = models.ForeignKey(Inwestycja, related_name="oferty", on_delete=models.CASCADE)
    
    adres = models.CharField(max_length=255)
    metraz = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    pokoje = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="dostępne")
    data_dodania = models.DateTimeField(auto_now_add=True)
    zdjecie = models.ImageField(upload_to="inwestycje/", blank=True, null=True)
    numer_lokalu = models.CharField(max_length=50, blank=True, null=True, help_text="Numer lub nazwa lokalu")
    numer_oferty = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="Numer Oferty")
    rodzaj_lokalu = models.ForeignKey('RodzajLokalu', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Rodzaj Lokalu")

    def __str__(self):
        return f"{self.adres}, {self.id}, ({self.metraz} m², {self.pokoje} pok.)"

class Rzut(models.Model):
    oferta = models.ForeignKey(Oferta, related_name="rzuty", on_delete=models.CASCADE)
    zdjecie = models.ImageField(upload_to="rzuty/")

class Cena(models.Model):
    oferta = models.ForeignKey(Oferta, related_name="ceny", on_delete=models.CASCADE)
    kwota = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateField()

    class Meta:
        ordering = ["data"]

    def __str__(self):
        return f"{self.kwota} zł ({self.data})"



class InwestycjaZdjecie(models.Model):
    inwestycja = models.ForeignKey('Inwestycja', related_name="zdjecia", on_delete=models.CASCADE)
    obraz = models.ImageField(upload_to="inwestycje/galeria/")

    def __str__(self):
        # A simple, safe representation.
        if self.inwestycja:
            return f"Zdjęcie {self.id} - {self.inwestycja.nazwa}"
        return f"Zdjęcie {self.id} (no related investment)"
    
class RodzajLokalu(models.Model):
        nazwa = models.CharField(max_length=100, unique=True, verbose_name="Rodzaj Lokalu")
        def __str__(self):
            return self.nazwa

        class Meta:
            verbose_name_plural = "Rodzaje Lokali"

class PomieszczeniePrzynalezne(models.Model):
    oferta = models.ForeignKey('Oferta', on_delete=models.CASCADE, related_name='pomieszczenia_przynalezne')
    nazwa = models.CharField(max_length=200, verbose_name="Nazwa Pomieszczenia")
    powierzchnia = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Powierzchnia (m²)")
    cena = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Cena")

    def __str__(self):
        return f"{self.nazwa} - {self.oferta.numer_lokalu}"

class SwiadczeniePieniezne(models.Model):
    oferta = models.ForeignKey('Oferta', on_delete=models.CASCADE, related_name='inne_swiadczenia')
    nazwa = models.CharField(max_length=200, verbose_name="Nazwa Świadczenia")
    kwota = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Kwota")
    opis = models.TextField(null=True, blank=True, verbose_name="Opis")

    def __str__(self):
        return f"{self.nazwa} - {self.kwota} zł"

class Rabat(models.Model):
    oferta = models.ForeignKey('Oferta', on_delete=models.CASCADE, related_name='rabaty')
    nazwa = models.CharField(max_length=200, verbose_name="Nazwa Rabatu/Promocji")
    wartosc = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Wartość (PLN)")
    typ = models.CharField(max_length=50, choices=[('procentowy', 'Procentowy'), ('kwotowy', 'Kwotowy')], verbose_name="Typ")
    data_od = models.DateField(verbose_name="Data rozpoczęcia")
    data_do = models.DateField(verbose_name="Data zakończenia")

    def __str__(self):
        return f"{self.nazwa} - {self.wartosc}"