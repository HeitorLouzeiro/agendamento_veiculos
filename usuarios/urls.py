from django.urls import path

from .views import (CustomLoginView, CustomLogoutView, alterar_senha,
                    confirmar_email, criar_motorista, criar_professor,
                    desativar_motorista, desativar_professor,
                    editar_motorista, editar_perfil, editar_professor,
                    lista_motoristas, lista_professores,
                    recuperar_senha_step1, recuperar_senha_step2,
                    recuperar_senha_step3, registro,
                    reenviar_email_confirmacao)

app_name = 'usuarios'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('registro/', registro, name='registro'),
    path('ativar-conta/<str:token>/', confirmar_email, name='ativar_conta'),
    path('reenviar-ativacao/', reenviar_email_confirmacao,
         name='reenviar_confirmacao'),

    # Recuperação de senha
    path('recuperar-senha/', recuperar_senha_step1,
         name='recuperar_senha_step1'),
    path('recuperar-senha/perguntas/', recuperar_senha_step2,
         name='recuperar_senha_step2'),
    path('recuperar-senha/nova-senha/', recuperar_senha_step3,
         name='recuperar_senha_step3'),

    # Perfil do usuário
    path('perfil/', editar_perfil, name='editar_perfil'),
    path('perfil/alterar-senha/', alterar_senha, name='alterar_senha'),

    # Gerenciamento de motoristas (responsável de campus)
    path('motoristas/', lista_motoristas, name='lista_motoristas'),
    path('motoristas/novo/', criar_motorista, name='criar_motorista'),
    path('motoristas/<uuid:uuid>/editar/', editar_motorista,
         name='editar_motorista'),
    path('motoristas/<uuid:uuid>/desativar/', desativar_motorista,
         name='desativar_motorista'),

    # Gerenciamento de professores (responsável de campus / admin)
    path('professores/', lista_professores, name='lista_professores'),
    path('professores/novo/', criar_professor, name='criar_professor'),
    path('professores/<uuid:uuid>/editar/', editar_professor,
         name='editar_professor'),
    path('professores/<uuid:uuid>/desativar/', desativar_professor,
         name='desativar_professor'),
]
