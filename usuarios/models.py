import uuid as _uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string


class Usuario(AbstractUser):
    """
    Model customizado de usuário.
    Usa grupos Django para diferenciar Professor, Administrador,
    Motorista e Responsável de Campus.
    """
    uuid = models.UUIDField(
        default=_uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name='UUID'
    )

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

    campus = models.ForeignKey(
        'campus.Campus',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios',
        verbose_name='Campus'
    )

    numero_habilitacao = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Número da CNH'
    )

    token_ativacao = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Token de Ativação'
    )
    token_criado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Token Criado Em'
    )

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
        grupo = self.groups.first()
        grupo_nome = grupo.name if grupo else 'Sem grupo'
        return f'{self.get_full_name()} ({grupo_nome})'

    def is_administrador(self):
        return self.is_superuser or self.groups.filter(
            name='Administradores'
        ).exists()

    def is_professor(self):
        return self.groups.filter(name='Professores').exists()

    def is_motorista(self):
        return self.groups.filter(name='Motoristas').exists()

    def is_responsavel_campus(self):
        return self.groups.filter(name='Responsaveis de Campus').exists()

    def gerar_token_ativacao(self):
        from django.utils import timezone
        self.token_ativacao = get_random_string(64)
        self.token_criado_em = timezone.now()
        return self.token_ativacao
