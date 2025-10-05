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

    # Sobrescreve o campo email para torná-lo único e obrigatório
    email = models.EmailField(
        verbose_name='E-mail',
        unique=True,
        error_messages={
            'unique': 'Este e-mail já está cadastrado.',
        }
    )

    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefone'
    )

    # Perguntas de segurança para recuperação de senha
    pergunta_seguranca_1 = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Pergunta de Segurança 1'
    )
    resposta_seguranca_1 = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Resposta de Segurança 1'
    )

    pergunta_seguranca_2 = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Pergunta de Segurança 2'
    )
    resposta_seguranca_2 = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Resposta de Segurança 2'
    )

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
