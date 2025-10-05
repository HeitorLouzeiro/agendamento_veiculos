import uuid

from django.db import models


class Curso(models.Model):
    """
    Model para representar cursos que utilizam veículos.
    Cada curso tem um limite mensal de quilometragem.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID'
    )
    nome = models.CharField(max_length=200, unique=True,
                            verbose_name='Nome do Curso')
    limite_km_mensal = models.PositiveIntegerField(
        default=1000,
        verbose_name='Limite de KM Mensal',
        help_text='Limite de quilometragem mensal para o curso'
    )
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(
        auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def get_km_utilizados_mes(self, ano, mes):
        """
        Retorna a quilometragem total utilizada pelo curso em um mês específico.
        Considera apenas agendamentos APROVADOS.
        """
        from django.db.models import Sum

        from agendamentos.models import Agendamento

        agendamentos = Agendamento.objects.filter(
            curso=self,
            status='aprovado',
            data_inicio__year=ano,
            data_inicio__month=mes
        )

        total_km = 0
        for agendamento in agendamentos:
            total_km += agendamento.get_total_km()

        return total_km

    def get_km_disponiveis_mes(self, ano, mes):
        """Retorna a quilometragem disponível no mês"""
        utilizados = self.get_km_utilizados_mes(ano, mes)
        return self.limite_km_mensal - utilizados
