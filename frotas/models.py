import uuid

from django.conf import settings
from django.db import models


class Abastecimento(models.Model):
    COMBUSTIVEL_CHOICES = [
        ('gasolina', 'Gasolina'),
        ('etanol', 'Etanol'),
        ('diesel', 'Diesel'),
        ('gnv', 'GNV'),
        ('eletrico', 'Elétrico'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trajeto = models.ForeignKey(
        'agendamentos.Trajeto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='abastecimentos',
        verbose_name='Trajeto Atribuído',
    )
    veiculo = models.ForeignKey(
        'veiculos.Veiculo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='abastecimentos',
        verbose_name='Veículo',
    )
    motorista = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='abastecimentos',
        verbose_name='Motorista',
    )
    agendamento = models.ForeignKey(
        'agendamentos.Agendamento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='abastecimentos',
        verbose_name='Agendamento Relacionado',
    )
    local_posto = models.CharField(max_length=200, verbose_name='Local / Nome do Posto')
    data_hora = models.DateTimeField(verbose_name='Data e Hora')
    km_atual = models.PositiveIntegerField(verbose_name='Km Atual do Veículo')
    litros_abastecidos = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name='Litros Abastecidos'
    )
    valor_gasto = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Valor Gasto (R$)'
    )
    tipo_combustivel = models.CharField(
        max_length=20,
        choices=COMBUSTIVEL_CHOICES,
        default='gasolina',
        verbose_name='Tipo de Combustível',
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Abastecimento'
        verbose_name_plural = 'Abastecimentos'
        ordering = ['-data_hora']

    def __str__(self):
        return f'{self.veiculo.placa} — {self.data_hora:%d/%m/%Y %H:%M} — R$ {self.valor_gasto}'

    @property
    def preco_por_litro(self):
        if self.litros_abastecidos:
            return round(float(self.valor_gasto) / float(self.litros_abastecidos), 3)
        return None


class Deslocamento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    motorista = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='deslocamentos',
        verbose_name='Motorista',
    )
    trajeto = models.ForeignKey(
        'agendamentos.Trajeto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deslocamentos',
        verbose_name='Trajeto Atribuído',
    )
    veiculo = models.ForeignKey(
        'veiculos.Veiculo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deslocamentos',
        verbose_name='Veículo',
    )
    agendamento = models.ForeignKey(
        'agendamentos.Agendamento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deslocamentos',
        verbose_name='Agendamento Relacionado',
    )
    origem = models.CharField(max_length=200, blank=True, verbose_name='Origem')
    destino = models.CharField(max_length=200, verbose_name='Destino')
    data_hora_saida = models.DateTimeField(verbose_name='Data/Hora de Saída')
    data_hora_chegada = models.DateTimeField(
        null=True, blank=True, verbose_name='Data/Hora de Chegada'
    )
    km_saida = models.PositiveIntegerField(verbose_name='Km na Saída')
    km_chegada = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='Km na Chegada'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Deslocamento'
        verbose_name_plural = 'Deslocamentos'
        ordering = ['-data_hora_saida']

    def __str__(self):
        dt = self.data_hora_saida.strftime('%d/%m/%Y %H:%M')
        return f'{self.veiculo.placa} → {self.destino} — {dt}'

    @property
    def km_percorridos(self):
        if self.km_chegada is not None and self.km_saida is not None:
            return self.km_chegada - self.km_saida
        return None


class Ocorrencia(models.Model):
    TIPO_CHOICES = [
        ('acidente', 'Acidente'),
        ('pane', 'Pane Mecânica'),
        ('multa', 'Multa de Trânsito'),
        ('furto', 'Furto / Roubo'),
        ('avaria', 'Avaria / Dano'),
        ('outro', 'Outro'),
    ]
    GRAVIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trajeto = models.ForeignKey(
        'agendamentos.Trajeto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ocorrencias',
        verbose_name='Trajeto Atribuído',
    )
    agendamento = models.ForeignKey(
        'agendamentos.Agendamento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ocorrencias',
        verbose_name='Agendamento',
    )
    veiculo = models.ForeignKey(
        'veiculos.Veiculo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ocorrencias',
        verbose_name='Veículo',
    )
    motorista = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ocorrencias',
        verbose_name='Motorista / Responsável',
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo de Ocorrência')
    gravidade = models.CharField(
        max_length=10, choices=GRAVIDADE_CHOICES, default='media', verbose_name='Gravidade'
    )
    data_hora = models.DateTimeField(verbose_name='Data e Hora da Ocorrência')
    local = models.CharField(max_length=200, verbose_name='Local da Ocorrência')
    descricao = models.TextField(verbose_name='Descrição da Ocorrência')
    providencias_tomadas = models.TextField(blank=True, verbose_name='Providências Tomadas')
    numero_boletim = models.CharField(
        max_length=50, blank=True, verbose_name='Nº Boletim de Ocorrência (BO)'
    )
    resolvido = models.BooleanField(default=False, verbose_name='Resolvido')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Ocorrência'
        verbose_name_plural = 'Ocorrências'
        ordering = ['-data_hora']

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.veiculo.placa} — {self.data_hora:%d/%m/%Y}'
