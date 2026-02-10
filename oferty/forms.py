from django import forms
from .models import Oferta, Cena

class OfertaForm(forms.ModelForm):
    class Meta:
        model = Oferta
        fields = ['adres', 'metraz', 'pokoje', 'status']  


class CenaForm(forms.ModelForm):
    class Meta:
        model = Cena
        fields = ['oferta', 'kwota', 'data']