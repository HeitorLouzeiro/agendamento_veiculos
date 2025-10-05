from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Model customizado de usuário.
    Usa grupos Django para diferenciar Professor e Administrador.
    """
    TIPO_USUARIO_CHOICES = [
        ('professor', 'Professor'),
        ('administrador', 'Administrador'),
    ]
    
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default='professor',
        verbose_name='Tipo de Usuário'
    )
    
    telefone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_tipo_usuario_display()})"
    
    def is_administrador(self):
        """Verifica se o usuário é administrador"""
        return self.tipo_usuario == 'administrador' or self.is_superuser
    
    def is_professor(self):
        """Verifica se o usuário é professor"""
        return self.tipo_usuario == 'professor'
