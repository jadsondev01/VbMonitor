from django import forms
from .models import Pauta, Municipio

# ===================== PAUTA =====================
class PautaForm(forms.ModelForm):
    class Meta:
        model = Pauta
        fields = ['nome']  # adicione outros campos existentes no modelo se houver

# ===================== MUNICÍPIO =====================
class MunicipioForm(forms.ModelForm):
    class Meta:
        model = Municipio
        fields = ['nome']  # somente campos existentes no modelo
