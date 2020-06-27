from django.urls import path
from . import views

app_name = 'encuestas'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetalleView.as_view(), name='detalle'),
    path('<int:pk>/resultado/', views.ResultadoView.as_view(), name='resultado'),
    path('<int:encuesta_id>/voto/', views.voto, name='voto'),
    path('sugerencias/', views.sugerencia, name='sugerencias'),
    path('sugerencia-enviada/', views.sugerencia_enviada, name='sugerencia-enviada'),
]