from django.urls import path

from . import views

app_name = 'agendamentos'

urlpatterns = [
    path('', views.lista_agendamentos, name='lista'),
    path('novo/', views.criar_agendamento, name='criar'),
    path('<uuid:pk>/', views.detalhe_agendamento, name='detalhe'),
    path('<uuid:pk>/editar/', views.editar_agendamento, name='editar'),
    path('<uuid:pk>/deletar/', views.deletar_agendamento, name='deletar'),
    path('aprovacao/', views.aprovacao_agendamentos, name='aprovacao'),
    path('<uuid:pk>/aprovar/', views.aprovar_agendamento, name='aprovar'),
    path('<uuid:pk>/reprovar/', views.reprovar_agendamento, name='reprovar'),
    path('json/', views.agendamentos_json, name='json'),
]
