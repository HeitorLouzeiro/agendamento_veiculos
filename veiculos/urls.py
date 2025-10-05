from django.urls import path
from . import views

app_name = 'veiculos'

urlpatterns = [
    path('', views.lista_veiculos, name='lista'),
    path('novo/', views.criar_veiculo, name='criar'),
    path('<int:pk>/editar/', views.editar_veiculo, name='editar'),
    path('<int:pk>/deletar/', views.deletar_veiculo, name='deletar'),
]
