from django.contrib import admin
from .models import Fonte, Municipio, Pauta, Noticia, ClassificacaoPauta, ClassificacaoMunicipio

admin.site.register(Fonte)
admin.site.register(Municipio)
admin.site.register(Pauta)
admin.site.register(Noticia)
admin.site.register(ClassificacaoPauta)
admin.site.register(ClassificacaoMunicipio)