from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    PERFIL_CHOICES = [
        ('JORNALISTA', 'Jornalista'),
        ('COORDENACAO', 'Coordenação/Editor-chefe'),
        ('ESTAGIARIO', 'Estagiário'),
    ]
    
    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES)
    ativo = models.BooleanField(default=True)
    dois_fatores = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'usuario'
    
    def __str__(self):
        return f"{self.username} ({self.perfil})"