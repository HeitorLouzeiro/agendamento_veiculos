"""
Configuração do app Common.
"""
from django.apps import AppConfig


class CommonConfig(AppConfig):
    """Configuração do app de funcionalidades comuns."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'common'
    verbose_name = 'Comum'
