from django.urls import path

from . import views

app_name = 'frotas'

urlpatterns = [
    # Dashboards
    path('motorista/', views.dashboard_motorista, name='dashboard_motorista'),
    path('responsavel/', views.dashboard_responsavel, name='dashboard_responsavel'),

    # Deslocamentos
    path('deslocamentos/ajax/salvar/',
         views.ajax_salvar_deslocamento,
         name='ajax_salvar_deslocamento'),
    path('deslocamentos/trajeto/<uuid:pk>/detalhes/',
         views.trajeto_detalhes_json,
         name='trajeto_detalhes_json'),
    path('deslocamentos/', views.lista_deslocamentos, name='lista_deslocamentos'),
    path('deslocamentos/novo/', views.criar_deslocamento, name='criar_deslocamento'),
    path('deslocamentos/<uuid:pk>/', views.detalhe_deslocamento, name='detalhe_deslocamento'),
    path('deslocamentos/<uuid:pk>/editar/', views.editar_deslocamento, name='editar_deslocamento'),
    path('deslocamentos/<uuid:pk>/deletar/', views.deletar_deslocamento, name='deletar_deslocamento'),

    # Abastecimentos
    path('abastecimentos/', views.lista_abastecimentos, name='lista_abastecimentos'),
    path('abastecimentos/novo/', views.criar_abastecimento, name='criar_abastecimento'),
    path('abastecimentos/<uuid:pk>/', views.detalhe_abastecimento, name='detalhe_abastecimento'),
    path('abastecimentos/<uuid:pk>/editar/', views.editar_abastecimento, name='editar_abastecimento'),
    path('abastecimentos/<uuid:pk>/deletar/', views.deletar_abastecimento, name='deletar_abastecimento'),

    # Ocorrências
    path('ocorrencias/', views.lista_ocorrencias, name='lista_ocorrencias'),
    path('ocorrencias/nova/', views.criar_ocorrencia, name='criar_ocorrencia'),
    path('ocorrencias/<uuid:pk>/', views.detalhe_ocorrencia, name='detalhe_ocorrencia'),
    path('ocorrencias/<uuid:pk>/editar/', views.editar_ocorrencia, name='editar_ocorrencia'),
    path('ocorrencias/<uuid:pk>/deletar/', views.deletar_ocorrencia, name='deletar_ocorrencia'),
    path('ocorrencias/<uuid:pk>/resolver/', views.resolver_ocorrencia, name='resolver_ocorrencia'),

    # Boletim Diário
    path('boletim/', views.boletim_diario, name='boletim_diario'),
    path('boletim/exportar/pdf/', views.exportar_boletim_pdf,
         name='exportar_boletim_pdf'),
]
