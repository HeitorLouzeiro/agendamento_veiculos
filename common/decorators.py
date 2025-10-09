"""
Decorators compartilhados para views.

Este módulo centraliza decoradores reutilizáveis em todo o projeto,
seguindo o princípio DRY (Don't Repeat Yourself).
"""

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def is_administrador(user):
    """
    Verifica se o usuário é administrador.

    Args:
        user: Objeto User do Django

    Returns:
        bool: True se o usuário é administrador, False caso contrário
    """
    return user.is_administrador()


def administrador_required(view_func):
    """
    Decorator que exige que o usuário seja administrador.

    Usage:
        @login_required
        @administrador_required
        def minha_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_administrador():
            messages.error(
                request,
                'Você não tem permissão para acessar esta página.'
            )
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
