import uuid

from django.db import models
from django.db.models import Q

from agendamentos.models import Agendamento


class Veiculo(models.Model):
    """
    Model para representar veículos disponíveis para agendamento.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID'
    )
    placa = models.CharField(max_length=10, unique=True, verbose_name='Placa')
    modelo = models.CharField(max_length=100, verbose_name='Modelo')
    marca = models.CharField(max_length=100, verbose_name='Marca')
    ano = models.PositiveIntegerField(verbose_name='Ano')
    cor = models.CharField(max_length=50, blank=True, verbose_name='Cor')
    capacidade_passageiros = models.PositiveIntegerField(
        default=5,
        verbose_name='Capacidade de Passageiros'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(
        auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'
        ordering = ['placa']

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo}"

    def tem_conflito(self, data_inicio, data_fim, agendamento_id=None):
        """
        Verifica se há conflito de agendamento para este veículo
        no período especificado.
        Agendamentos aprovados E pendentes são considerados conflitos,
        pois o veículo fica reservado enquanto aguarda aprovação.

        Args:
            data_inicio: Data/hora de início do agendamento
            data_fim: Data/hora de fim do agendamento
            agendamento_id: ID do agendamento atual (para edição)

        Returns:
            True se houver conflito, False caso contrário
        """

        # Query para verificar sobreposição de datas
        # Agendamentos APROVADOS e PENDENTES bloqueiam o veículo
        conflitos = Agendamento.objects.filter(
            veiculo=self,
            # Aprovados e pendentes bloqueiam
            status__in=['aprovado', 'pendente']
        ).filter(
            Q(data_inicio__lt=data_fim) & Q(data_fim__gt=data_inicio)
        )

        # Exclui o próprio agendamento se estiver editando
        if agendamento_id:
            conflitos = conflitos.exclude(id=agendamento_id)

        return conflitos.exists()

    def get_agendamentos_periodo(self, data_inicio, data_fim):
        """
        Retorna agendamentos aprovados e pendentes do veículo em um período.
        Agendamentos aprovados e pendentes são considerados para verificação
        de conflito, pois o veículo fica reservado enquanto aguarda decisão.
        """

        return Agendamento.objects.filter(
            veiculo=self,
            status__in=['aprovado', 'pendente']  # Aprovados e pendentes
        ).filter(
            Q(data_inicio__lt=data_fim) & Q(data_fim__gt=data_inicio)
        ).order_by('data_inicio')
