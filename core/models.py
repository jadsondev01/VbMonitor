from django.db import models

class Fonte(models.Model):
    TIPO_COLETA_CHOICES = [
        ('RSS', 'RSS'),
        ('API', 'API'),
        ('SCRAPING', 'Scraping'),
    ]
    
    nome = models.CharField(max_length=200)
    url_base = models.URLField(unique=True, max_length=500)
    tipo_coleta = models.CharField(max_length=20, choices=TIPO_COLETA_CHOICES)
    url_rss_api = models.URLField(max_length=500, null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nome

class Municipio(models.Model):
    id_municipio = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=100, unique=True)
    regiao = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return self.nome

class Pauta(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.nome

class Noticia(models.Model):
    titulo = models.CharField(max_length=500)
    url = models.URLField(unique=True, max_length=1000)
    fonte = models.ForeignKey(Fonte, on_delete=models.CASCADE)
    data_publicacao = models.DateTimeField()
    conteudo = models.TextField()
    texto_resumo = models.TextField()
    coletado_em = models.DateTimeField(auto_now_add=True)
    deduplicado = models.BooleanField(default=False)
    acessos = models.IntegerField(default=0)
    
    def __str__(self):
        return self.titulo[:100]

class ClassificacaoPauta(models.Model):
    METODO_CHOICES = [
        ('AUTOMATICO', 'Automático'),
        ('MANUAL', 'Manual'),
    ]
    
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE)
    pauta = models.ForeignKey(Pauta, on_delete=models.CASCADE)
    metodo_classificacao = models.CharField(max_length=20, choices=METODO_CHOICES)
    data_classificacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('noticia', 'pauta')

class ClassificacaoMunicipio(models.Model):
    METODO_CHOICES = [
        ('AUTOMATICO', 'Automático'),
        ('MANUAL', 'Manual'),
    ]
    
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    metodo_classificacao = models.CharField(max_length=20, choices=METODO_CHOICES)
    data_classificacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('noticia', 'municipio')