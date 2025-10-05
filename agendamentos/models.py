import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Agendamento(models.Model):
    """
    Model para representar agendamentos de veículos por cursos.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('reprovado', 'Reprovado'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID'
    )
    curso = models.ForeignKey(
        'cursos.Curso',
        on_delete=models.CASCADE,
        related_name='agendamentos',
        verbose_name='Curso'
    )
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='agendamentos',
        verbose_name='Professor'
    )
    veiculo = models.ForeignKey(
        'veiculos.Veiculo',
        on_delete=models.CASCADE,
        related_name='agendamentos',
        verbose_name='Veículo'
    )
    data_inicio = models.DateTimeField(verbose_name='Data/Hora de Início')
    data_fim = models.DateTimeField(verbose_name='Data/Hora de Fim')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name='Status'
    )
    motivo_reprovacao = models.TextField(
        blank=True,
        verbose_name='Motivo da Reprovação'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    criado_em = models.DateTimeField(
        auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(
        auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['-data_inicio']

    def __str__(self):
        try:
            curso_nome = self.curso.nome if self.curso else "Curso não definido"
            veiculo_placa = self.veiculo.placa if self.veiculo else "Veículo não definido"
            return f"{curso_nome} - {veiculo_placa} ({self.get_status_display()})"
        except AttributeError:
            return f"Agendamento {self.id or 'novo'}"

    def get_total_km(self):
        """Retorna a quilometragem total de todos os trajetos do agendamento"""
        return sum(trajeto.quilometragem for trajeto in self.trajetos.all())

    def clean(self):
        """Validações do model"""
        super().clean()

        # Validação 1: Data fim deve ser maior que data início
        if self.data_fim and self.data_inicio and self.data_fim <= self.data_inicio:
            raise ValidationError({
                'data_fim': 'A data de fim deve ser posterior à data de início.'
            })

        # Validação 2: Verificar conflito de veículo
        if self.veiculo_id and self.data_inicio and self.data_fim:
            try:
                veiculo = self.veiculo
                if veiculo.tem_conflito(self.data_inicio, self.data_fim, self.id):
                    conflitos = veiculo.get_agendamentos_periodo(
                        self.data_inicio, self.data_fim)
                    if self.id:
                        conflitos = conflitos.exclude(id=self.id)

                    mensagem = f"O veículo {veiculo.placa} já está agendado neste período:"
                    for conflito in conflitos:
                        mensagem += f"\n- {conflito.data_inicio.strftime('%d/%m/%Y %H:%M')} até {conflito.data_fim.strftime('%d/%m/%Y %H:%M')} ({conflito.curso.nome})"

                    raise ValidationError({
                        'veiculo': mensagem
                    })
            except AttributeError:
                # Se o veículo não existe, deixa passar para outras validações capturarem
                pass

    def validar_limite_km(self):
        """
        Valida se o agendamento ultrapassa o limite mensal de KM do curso.
        Deve ser chamado após os trajetos serem salvos.
        """
        if self.status == 'aprovado' and self.curso_id and self.data_inicio:
            try:
                curso = self.curso
                ano = self.data_inicio.year
                mes = self.data_inicio.month

                # Calcula KM já utilizados no mês (excluindo este agendamento)
                km_utilizados = curso.get_km_utilizados_mes(ano, mes)

                # Se estiver editando, subtrai os KM antigos deste agendamento
                if self.id:
                    agendamento_antigo = Agendamento.objects.filter(
                        id=self.id,
                        status='aprovado'
                    ).first()
                    if agendamento_antigo:
                        km_utilizados -= agendamento_antigo.get_total_km()

                # Adiciona os KM deste agendamento
                total_km = self.get_total_km()
                km_total = km_utilizados + total_km

                if km_total > curso.limite_km_mensal:
                    km_disponiveis = curso.limite_km_mensal - km_utilizados
                    raise ValidationError(
                        f"Este agendamento ultrapassa o limite mensal de {curso.limite_km_mensal} km do curso {curso.nome}. "
                        f"KM já utilizados no mês: {km_utilizados} km. "
                        f"KM disponíveis: {km_disponiveis} km. "
                        f"KM solicitados: {total_km} km."
                    )
            except AttributeError:
                # Se não conseguir acessar curso, pula a validação
                pass

    def aprovar(self):
        """Aprova o agendamento após validar limite de KM"""
        self.status = 'aprovado'
        self.motivo_reprovacao = ''
        self.validar_limite_km()  # Valida antes de aprovar
        self.save()

    def reprovar(self, motivo):
        """Reprova o agendamento"""
        self.status = 'reprovado'
        self.motivo_reprovacao = motivo
        self.save()


class Trajeto(models.Model):
    """
    Model para representar trajetos de um agendamento.
    Um agendamento pode ter múltiplos trajetos.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID'
    )
    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.CASCADE,
        related_name='trajetos',
        verbose_name='Agendamento'
    )
    origem = models.CharField(max_length=200, verbose_name='Origem')
    destino = models.CharField(max_length=200, verbose_name='Destino')
    data_saida = models.DateTimeField(verbose_name='Data/Hora de Saída')
    data_chegada = models.DateTimeField(verbose_name='Data/Hora de Chegada')
    quilometragem = models.PositiveIntegerField(
        verbose_name='Quilometragem (km)')
    descricao = models.TextField(verbose_name='Descrição/Objetivo do Trajeto')

    class Meta:
        verbose_name = 'Trajeto'
        verbose_name_plural = 'Trajetos'
        ordering = ['data_saida']

    def __str__(self):
        return f"{self.origem} → {self.destino} ({self.quilometragem} km)"

    def clean(self):
        """Validações do model"""
        super().clean()

        # Validação: Data chegada deve ser maior que data saída
        if self.data_chegada and self.data_saida and self.data_chegada <= self.data_saida:
            raise ValidationError({
                'data_chegada': 'A data de chegada deve ser posterior à data de saída.'
            })

        # Validação: Trajeto deve estar dentro do período do agendamento
        if self.agendamento_id and self.data_saida and self.data_chegada:
            if self.data_saida < self.agendamento.data_inicio:
                raise ValidationError({
                    'data_saida': 'A data de saída não pode ser anterior ao início do agendamento.'
                })
            if self.data_chegada > self.agendamento.data_fim:
                raise ValidationError({
                    'data_chegada': 'A data de chegada não pode ser posterior ao fim do agendamento.'
                })
