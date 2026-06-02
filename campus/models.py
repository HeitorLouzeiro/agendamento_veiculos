import uuid

from django.db import models


class Campus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=200, unique=True, verbose_name='Nome do Campus')
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    endereco = models.CharField(max_length=300, blank=True, verbose_name='Endereço')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Campus'
        verbose_name_plural = 'Campi'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} — {self.cidade}'
