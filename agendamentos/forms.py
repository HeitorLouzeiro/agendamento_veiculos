from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.utils import timezone

from cursos.models import Curso
from veiculos.models import Veiculo

from .models import Agendamento, Trajeto


class AgendamentoForm(forms.ModelForm):
    """Formulário para criar/editar agendamentos"""

    class Meta:
        model = Agendamento
        fields = ['curso', 'veiculo', 'data_inicio', 'data_fim', 'observacoes']
        widgets = {
            'curso': forms.Select(attrs={'class': 'form-select'}),
            'veiculo': forms.Select(attrs={'class': 'form-select'}),
            'data_inicio': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'data_fim': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'observacoes': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Filtra apenas cursos e veículos ativos
        self.fields['curso'].queryset = Curso.objects.filter(ativo=True)
        self.fields['veiculo'].queryset = Veiculo.objects.filter(ativo=True)

        # Formata as datas para o formato datetime-local ao editar
        if self.instance and self.instance.pk:
            if self.instance.data_inicio:
                # Converte para timezone local antes de formatar
                data_local = timezone.localtime(self.instance.data_inicio)
                # Formato ISO 8601 (YYYY-MM-DDThh:mm) sem timezone
                data_inicio_fmt = data_local.strftime('%Y-%m-%dT%H:%M')
                self.initial['data_inicio'] = data_inicio_fmt
            if self.instance.data_fim:
                # Converte para timezone local antes de formatar
                data_local = timezone.localtime(self.instance.data_fim)
                data_fim_fmt = data_local.strftime('%Y-%m-%dT%H:%M')
                self.initial['data_fim'] = data_fim_fmt

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        veiculo = cleaned_data.get('veiculo')

        # Validação de datas
        if data_inicio and data_fim and data_fim <= data_inicio:
            raise ValidationError({
                'data_fim': (
                    'A data de fim deve ser posterior à data de início.'
                )
            })

        # Validação de conflito de veículo
        if veiculo and data_inicio and data_fim:
            agendamento_id = self.instance.id if self.instance else None
            if veiculo.tem_conflito(data_inicio, data_fim, agendamento_id):
                conflitos = veiculo.get_agendamentos_periodo(
                    data_inicio, data_fim
                )
                if agendamento_id:
                    conflitos = conflitos.exclude(id=agendamento_id)

                msg = (
                    f"O veículo {veiculo.placa} já está "
                    f"agendado neste período:"
                )
                for conflito in conflitos:
                    dt_inicio = conflito.data_inicio.strftime(
                        '%d/%m/%Y %H:%M'
                    )
                    dt_fim = conflito.data_fim.strftime('%d/%m/%Y %H:%M')
                    msg += (
                        f"\n- {dt_inicio} até {dt_fim} "
                        f"({conflito.curso.nome})"
                    )

                raise ValidationError({
                    'veiculo': msg
                })

        # Validação de limite de KM do curso
        # (só se já temos o total de KM dos trajetos)
        curso = cleaned_data.get('curso')
        if curso and data_inicio and hasattr(self, '_trajetos_km'):
            total_km_trajetos = self._trajetos_km
            
            if total_km_trajetos > 0:  # Só valida se há KM para validar
                ano = data_inicio.year
                mes = data_inicio.month
                
                # Calcula KM já utilizados no mês
                km_utilizados = curso.get_km_utilizados_mes(ano, mes)
                
                # Se estiver editando, subtrai os KM antigos deste agendamento
                if self.instance and self.instance.id:
                    km_utilizados -= self.instance.get_total_km()
                
                # Verifica se excede o limite
                km_total = km_utilizados + total_km_trajetos
                
                if km_total > curso.limite_km_mensal:
                    km_disponiveis = curso.limite_km_mensal - km_utilizados
                    raise ValidationError({
                        'curso': (
                            f"Este agendamento ultrapassa o limite mensal "
                            f"de {curso.limite_km_mensal} km do curso "
                            f"{curso.nome}. "
                            f"KM já utilizados no mês: {km_utilizados} km. "
                            f"KM disponíveis: {km_disponiveis} km. "
                            f"KM solicitados: {total_km_trajetos} km."
                        )
                    })

        return cleaned_data
    
    def set_trajetos_km(self, total_km):
        """Método para definir o total de KM dos trajetos para validação"""
        self._trajetos_km = total_km
    
    def validar_limite_km_manual(self, total_km_trajetos):
        """
        Valida manualmente o limite de KM do curso.
        Usado quando precisamos validar antes de salvar.
        """
        if not self.cleaned_data:
            return
            
        curso = self.cleaned_data.get('curso')
        data_inicio = self.cleaned_data.get('data_inicio')
        
        if curso and data_inicio and total_km_trajetos > 0:
            ano = data_inicio.year
            mes = data_inicio.month
            
            # Calcula KM já utilizados no mês
            km_utilizados = curso.get_km_utilizados_mes(ano, mes)
            
            # Se estiver editando, subtrai os KM antigos deste agendamento
            if self.instance and self.instance.id:
                km_utilizados -= self.instance.get_total_km()
            
            # Verifica se excede o limite
            km_total = km_utilizados + total_km_trajetos
            
            if km_total > curso.limite_km_mensal:
                km_disponiveis = curso.limite_km_mensal - km_utilizados
                raise ValidationError(
                    f"Este agendamento ultrapassa o limite mensal de "
                    f"{curso.limite_km_mensal} km do curso {curso.nome}. "
                    f"KM já utilizados no mês: {km_utilizados} km. "
                    f"KM disponíveis: {km_disponiveis} km. "
                    f"KM solicitados: {total_km_trajetos} km."
                )


class TrajetoForm(forms.ModelForm):
    """Formulário para trajetos"""

    class Meta:
        model = Trajeto
        fields = [
            'origem', 'destino', 'data_saida',
            'data_chegada', 'quilometragem', 'descricao'
        ]
        widgets = {
            'origem': forms.TextInput(attrs={'class': 'form-control'}),
            'destino': forms.TextInput(attrs={'class': 'form-control'}),
            'data_saida': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'data_chegada': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'quilometragem': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),
            'descricao': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Formata as datas para o formato datetime-local ao editar
        if self.instance and self.instance.pk:
            if self.instance.data_saida:
                # Converte para timezone local antes de formatar
                data_local = timezone.localtime(self.instance.data_saida)
                data_saida_fmt = data_local.strftime('%Y-%m-%dT%H:%M')
                self.initial['data_saida'] = data_saida_fmt
            if self.instance.data_chegada:
                # Converte para timezone local antes de formatar
                data_local = timezone.localtime(self.instance.data_chegada)
                data_chegada_fmt = data_local.strftime('%Y-%m-%dT%H:%M')
                self.initial['data_chegada'] = data_chegada_fmt
                self.initial['data_chegada'] = data_chegada_fmt

    def clean(self):
        cleaned_data = super().clean()
        data_saida = cleaned_data.get('data_saida')
        data_chegada = cleaned_data.get('data_chegada')

        # Validação 1: Data chegada deve ser maior que data saída
        if data_saida and data_chegada and data_chegada <= data_saida:
            raise ValidationError({
                'data_chegada': (
                    'A data de chegada deve ser posterior à data de saída.'
                )
            })

        # Validação 2: Trajeto deve estar dentro do período do agendamento
        return cleaned_data


# Formset para criar agendamentos (2 formulários: ida e volta)
TrajetoFormSet = inlineformset_factory(
    Agendamento,
    Trajeto,
    form=TrajetoForm,
    extra=2,  # Exatamente 2 formulários vazios
    min_num=0,  # Sem mínimo forçado (extra já define 2)
    validate_min=False,
    can_delete=True
)

# Formset para editar agendamentos (sem formulários extras)
TrajetoFormSetEdit = inlineformset_factory(
    Agendamento,
    Trajeto,
    form=TrajetoForm,
    extra=0,  # Nenhum formulário extra ao editar
    min_num=1,  # Mínimo obrigatório: 1
    validate_min=True,
    can_delete=True
)
