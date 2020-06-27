import datetime

from django.db import models
from django.utils import timezone


class Pregunta(models.Model):
    pregunta_t = models.CharField(max_length=200)
    fecha_p = models.DateTimeField('Fecha de publicación')

    def __str__(self):
        return self.pregunta_t

    def publicaciones_recientes(self):
        return timezone.now() - datetime.timedelta(days=1) <= self.fecha_p <= timezone.now()


class Opcion(models.Model):
    encuesta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    opcion_t = models.CharField(max_length=200, null=True)
    voto = models.IntegerField(default=0)

    def __str__(self):
        return self.opcion_t