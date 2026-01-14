from django.db import models

class NoticiaAlerta(models.Model):
    titulo = models.CharField(max_length=255)
    link = models.URLField()
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
