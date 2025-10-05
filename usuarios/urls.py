from django.urls import path
from django.views.generic import RedirectView

from .views import (CustomLoginView, CustomLogoutView, alterar_senha,
                    editar_perfil, recuperar_senha_step1,
                    recuperar_senha_step2, recuperar_senha_step3, registro)

urlpatterns = [
    path(
        '',
        RedirectView.as_view(pattern_name='login', permanent=False),
        name='home'
    ),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('registro/', registro, name='registro'),

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
