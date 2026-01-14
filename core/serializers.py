from rest_framework import serializers
from .models import Noticia, Fonte, Municipio, Pauta

class FonteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fonte
        fields = '__all__'

class MunicipioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipio
        fields = '__all__'

class PautaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pauta
        fields = '__all__'

class NoticiaSerializer(serializers.ModelSerializer):
    fonte_nome = serializers.CharField(source='fonte.nome', read_only=True)
    
    class Meta:
        model = Noticia
        fields = '__all__'