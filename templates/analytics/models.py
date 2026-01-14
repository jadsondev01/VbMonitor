from django.db import models
from core.models import Noticia
from users.models import Usuario

class Busca(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    termo = models.CharField(max_length=255)
    filtros = models.JSONField(default=dict)
    resultados = models.IntegerField(default=0)
    realizada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username}: {self.termo}"


class HistoricoAcesso(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE)
    acessado_em = models.DateTimeField(auto_now_add=True)
    tempo_leitura = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('usuario', 'noticia')
