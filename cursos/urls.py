from django.urls import path
from . import views

app_name = 'cursos'

urlpatterns = [
    path('', views.lista_cursos, name='lista'),
    path('novo/', views.criar_curso, name='criar'),
    path('<int:pk>/editar/', views.editar_curso, name='editar'),
    path('<int:pk>/deletar/', views.deletar_curso, name='deletar'),
]
