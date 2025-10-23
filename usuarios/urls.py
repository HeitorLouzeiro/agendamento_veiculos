from django.urls import path

from .views import (CustomLoginView, CustomLogoutView, alterar_senha,
                    confirmar_email, editar_perfil, recuperar_senha_step1,
                    recuperar_senha_step2, recuperar_senha_step3, registro,
                    reenviar_email_confirmacao)

app_name = 'usuarios'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('registro/', registro, name='registro'),
    path('ativar-conta/<str:token>/', confirmar_email,
         name='ativar_conta'),
    path('reenviar-ativacao/', reenviar_email_confirmacao,
         name='reenviar_confirmacao'),

    # Recuperação de senha
    path(
        'recuperar-senha/',
        recuperar_senha_step1,
        name='recuperar_senha_step1'
    ),
    path(
        'recuperar-senha/perguntas/',
        recuperar_senha_step2,
        name='recuperar_senha_step2'
    ),
    path(
        'recuperar-senha/nova-senha/',
        recuperar_senha_step3,
        name='recuperar_senha_step3'
    ),

    # Perfil do usuário
    path('perfil/', editar_perfil, name='editar_perfil'),
    path('perfil/alterar-senha/', alterar_senha, name='alterar_senha'),
]
