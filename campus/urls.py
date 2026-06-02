from django.urls import path

from . import views

app_name = 'campus'

urlpatterns = [
    path('', views.lista_campi, name='lista'),
    path('novo/', views.criar_campus, name='criar'),
    path('<uuid:pk>/editar/', views.editar_campus, name='editar'),
    path('<uuid:pk>/deletar/', views.deletar_campus, name='deletar'),
]
