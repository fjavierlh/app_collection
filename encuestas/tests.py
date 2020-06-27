import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Pregunta


class PreguntaModelTest(TestCase):

    def test_publicaciones_futuras(self):
        """
        publicaciones_recientes() debe devolver False para encuestas cuya fecha_p esté en el futuro
        """
        tiempo = timezone.now() + datetime.timedelta(days=30)
        encuesta_futura = Pregunta(fecha_p=tiempo)
        return self.assertIs(encuesta_futura.publicaciones_recientes(), False)

    def test_publicaciones_recientes_encuesta_pasada(self):
        """
        publicaciones_recientes() devuelve False para encuestas cuya fecha_p sea de más de un día
        """
        tiempo = timezone.now() - datetime.timedelta(days=1, seconds=1)
        encuesta_pasada = Pregunta(fecha_p=tiempo)
        return self.assertIs(encuesta_pasada.publicaciones_recientes(), False)

    def test_publicaciones_recientes_encuesta_reciente(self):
        """
        publicaciones_recientes() debe devolver True para encuestas publicadas hace menos de un día
        """
        tiempo = timezone.now() - datetime.timedelta(hours=23, minutes=59)
        encuesta_reciente = Pregunta(fecha_p=tiempo)
        return self.assertIs(encuesta_reciente.publicaciones_recientes(), True)


def crear_encuesta(texto, dias, opcion):
    """
    Función para facilitar la creación de preguntas para test
    """
    tiempo = timezone.now() + datetime.timedelta(days=dias)
    encuesta = Pregunta.objects.create(pregunta_t=texto, fecha_p=tiempo)
    if opcion == True:
        encuesta.opcion_set.create(opcion_t="Foo")
    return encuesta


class EncuestasIndexViewTests(TestCase):

    def test_sin_encuestas(self):
        """
        Si no existe ninguna pregunta, aparece un mensaje aclaratorio.
        """
        respuesta = self.client.get(reverse('encuestas:index'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'No hay encuestas publicadas.')
        self.assertQuerysetEqual(respuesta.context['ls_ult_publ'], [])

    def test_encuesta_pasada(self):
        """
        Encuestas con fecha_p en el pasado aparecen en la página index.
        """
        crear_encuesta("Pregunta pasada.", -30, True)
        respuesta = self.client.get(reverse('encuestas:index'))
        self.assertQuerysetEqual(respuesta.context['ls_ult_publ'], ['<Pregunta: Pregunta pasada.>'])

    def test_encuesta_futura(self):
        """
         Encuestas con fecha_p en el futuro no aparecen en la página index
        """
        crear_encuesta("Pregunta futura", 30, True)
        respuesta = self.client.get(reverse('encuestas:index'))
        self.assertQuerysetEqual(respuesta.context['ls_ult_publ'], [])

    def test_encuesta_pasada_y_encuesta_futura(self):
        crear_encuesta("Pregunta pasada.", -30, True)
        crear_encuesta("Pregunta futura.", 30, True)
        respuesta = self.client.get(reverse('encuestas:index'))
        self.assertQuerysetEqual(respuesta.context['ls_ult_publ'], ['<Pregunta: Pregunta pasada.>'])

    def test_dos_encuestas_pasadas(self):
        crear_encuesta("Pregunta pasada 1.", -30, True)
        crear_encuesta("Pregunta pasada 2.", -15, True)
        respuesta = self.client.get(reverse('encuestas:index'))
        self.assertQuerysetEqual(respuesta.context['ls_ult_publ'],
                                 ['<Pregunta: Pregunta pasada 2.>', '<Pregunta: Pregunta pasada 1.>'])

    def test_dos_encuestas_futuras(self):
        crear_encuesta("Pregunta futura 1.", 30, True)
        crear_encuesta("Pregunta futura 2.", 15, True)
        respuesta = self.client.get(reverse('encuestas:index'))
        self.assertQuerysetEqual(respuesta.context['ls_ult_publ'], [])

    def test_pregunta_sin_opciones_futura(self):
        crear_encuesta("Pregunta sin opciones.", 30, False)
        respuesta = self.client.get(reverse('encuestas:index'))
        self.assertQuerysetEqual(respuesta.context['ls_ult_publ'], [])

    def test_pregunta_sin_opciones_pasada(self):
        crear_encuesta("Pregunta sin opciones.", -30, False)
        respuesta = self.client.get(reverse('encuestas:index'))
        self.assertQuerysetEqual(respuesta.context['ls_ult_publ'], [])

    def test_pregunta_con_opciones_futura(self):
        crear_encuesta("Pregunta con opciones.", 30, True)
        respuesta = self.client.get(reverse('encuestas:index'))
        self.assertQuerysetEqual(respuesta.context['ls_ult_publ'], [])

    def test_pregunta_con_opciones_pasada(self):
            crear_encuesta("Pregunta con opciones.", -30, True)
            respuesta = self.client.get(reverse('encuestas:index'))
            self.assertQuerysetEqual(respuesta.context['ls_ult_publ'], ['<Pregunta: Pregunta con opciones.>'])


class DetalleViewTest(TestCase):
    def test_encuesta_futura(self):
        pregunta_futura = crear_encuesta("Pregunta futura", 30, True)
        respuesta = self.client.get(reverse('encuestas:detalle', args=(pregunta_futura.id,)))
        self.assertEqual(respuesta.status_code, 404)

    def test_encuesta_pasada(self):
        pregunta_pasada = crear_encuesta("Pregunta pasada", -30, True)
        respuesta = self.client.get(reverse('encuestas:detalle', args=(pregunta_pasada.id,)))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, pregunta_pasada)

    def test_pregunta_sin_opciones_futura(self):
        pregunta_sin_opciones = crear_encuesta("Encuesta sin opciones", 30, False)
        respuesta = self.client.get(reverse('encuestas:detalle', args=(pregunta_sin_opciones.id,)))
        self.assertEqual(respuesta.status_code, 404)

    def test_pregunta_sin_opciones_futura(self):
        pregunta_con_opciones = crear_encuesta("Encuesta con opciones", -30, True)
        respuesta = self.client.get(reverse('encuestas:detalle', args=(pregunta_con_opciones.id,)))
        self.assertEqual(respuesta.status_code, 200)

class ResultadoViewTest(TestCase):
    def test_encuesta_futura(self):
        pregunta_futura = crear_encuesta("Pregunta futura", 30, True)
        respuesta = self.client.get(reverse('encuestas:resultado', args=(pregunta_futura.id,)))
        self.assertEqual(respuesta.status_code, 404)

    def test_encuesta_pasada(self):
        pregunta_pasada = crear_encuesta("Pregunta pasada", -30, True)
        respuesta = self.client.get(reverse('encuestas:resultado', args=(pregunta_pasada.id,)))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, pregunta_pasada)

    def test_pregunta_sin_opciones_futura(self):
        pregunta_sin_opciones = crear_encuesta("Encuesta sin opciones", 30, False)
        respuesta = self.client.get(reverse('encuestas:resultado', args=(pregunta_sin_opciones.id,)))
        self.assertEqual(respuesta.status_code, 404)

    def test_pregunta_sin_opciones_futura(self):
        pregunta_con_opciones = crear_encuesta("Encuesta con opciones", -30, True)
        respuesta = self.client.get(reverse('encuestas:resultado', args=(pregunta_con_opciones.id,)))
        self.assertEqual(respuesta.status_code, 200)
