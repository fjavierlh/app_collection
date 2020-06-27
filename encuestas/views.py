import datetime

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .forms import SugerenciaForm
from .models import Pregunta, Opcion


class IndexView(generic.ListView):
    paginate_by = 5
    template_name = 'encuestas/index.html'
    context_object_name = 'ls_ult_publ'

    def get_queryset(self):
        """Devuelve las últimas 5 publicaciones a fecha actual y las preguntas sin opciones"""
        return Pregunta.objects.exclude(opcion__opcion_t__exact=None).filter(fecha_p__lte=timezone.now()).order_by('-fecha_p')

class DetalleView(generic.DetailView):
    model = Pregunta
    template_name = 'encuestas/detalle.html'

    def get_queryset(self):
        """Excluye las preguntas SIN opciones y las publicadas en una fecha futura"""
        return Pregunta.objects.exclude(opcion__opcion_t__exact=None).filter(fecha_p__lte=timezone.now())

class ResultadoView(generic.DetailView):
    model = Pregunta
    template_name = 'encuestas/resultado.html'

    def get_queryset(self):
        """Excluye las preguntas SIN opciones y las publicadas en una fecha futura"""
        return Pregunta.objects.exclude(opcion__opcion_t__exact=None).filter(fecha_p__lte=timezone.now())

def voto(request, encuesta_id):
    pregunta = get_object_or_404(Pregunta, pk=encuesta_id)
    try:
        opcion_sel = pregunta.opcion_set.get(pk=request.POST['opcion'])
    except (KeyError, Opcion.DoesNotExist):
        return render(request, 'encuestas/detalle.html', { 'pregunta': pregunta, 'mensaje_error': "ERROR: Para votar debe selecionar una opción"})
    else:
        opcion_sel.voto += 1
        opcion_sel.save()
        return HttpResponseRedirect(reverse('encuestas:resultado', args=(pregunta.id,)))

def sugerencia(request):
    if request.POST == 'GET':
        formulario = SugerenciaForm()
    else:
        formulario = SugerenciaForm(request.POST)
        if formulario.is_valid():
            asunto = formulario.cleaned_data['nombre']
            correo = formulario.cleaned_data['email']
            mensaje = formulario.cleaned_data['sugerencia']
            try:
                send_mail(asunto, mensaje, correo, ['fjavierlh@gmail.com'])
            except BadHeaderError:
                render(request, 'encuestas/sugerencias.html', {'formulario': formulario, 'mensaje_error': "Header inválido encontrado."})
            return redirect('encuestas:sugerencia-enviada')
    return render(request, 'encuestas/sugerencias.html', {'formulario': formulario})

def sugerencia_enviada(request):
       return render(request, 'encuestas/sugerencia-enviada.html', {'mensaje': "Tu sugerencia se ha enviado con éxito"})
