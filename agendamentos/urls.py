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

    # Relatórios
    path('relatorios/', views.relatorio_geral, name='relatorio_geral'),
    path('relatorios/curso/', views.relatorio_por_curso,
         name='relatorio_por_curso'),
    path('relatorios/professor/', views.relatorio_por_professor,
         name='relatorio_por_professor'),

    # Exportações
    path('relatorios/exportar/excel/',
         views.exportar_relatorio_excel, name='exportar_excel'),
    path('relatorios/exportar/pdf/',
         views.exportar_relatorio_pdf, name='exportar_pdf'),
    path('relatorios/curso/exportar/excel/',
         views.exportar_curso_excel, name='exportar_curso_excel'),
]
