from rest_framework import serializers
from core.models import Noticia, ClassificacaoPauta, ClassificacaoMunicipio
from .models import Busca, HistoricoAcesso

class NoticiaDetalheSerializer(serializers.ModelSerializer):
    fonte_nome = serializers.CharField(source='fonte.nome', read_only=True)
    pautas = serializers.SerializerMethodField()
    municipios = serializers.SerializerMethodField()
    
    class Meta:
        model = Noticia
        fields = ['id', 'titulo', 'url', 'fonte_nome', 'data_publicacao', 
                 'conteudo', 'acessos', 'pautas', 'municipios', 'coletado_em']
    
    def get_pautas(self, obj):
        return list(obj.classificacaopauta_set.values_list('pauta__nome', flat=True))
    
    def get_municipios(self, obj):
        return list(obj.classificacaomunicipio_set.values_list('municipio__nome', flat=True))