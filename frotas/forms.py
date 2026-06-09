from django import forms
from django.utils import timezone

from agendamentos.models import Agendamento, Trajeto
from veiculos.models import Veiculo

from .models import Abastecimento, Deslocamento, Ocorrencia

_REQUIRED = 'Este campo é obrigatório.'
_INVALID_CHOICE = 'Selecione uma opção válida.'
_INVALID_NUMBER = 'Informe um número válido.'
_INVALID_DATETIME = 'Informe uma data e hora válidas (ex: 09/06/2026 14:30).'


class AbastecimentoForm(forms.ModelForm):
    class Meta:
        model = Abastecimento
        fields = [
            'trajeto',
            'veiculo', 'agendamento', 'local_posto', 'data_hora',
            'km_atual', 'litros_abastecidos', 'valor_gasto',
            'tipo_combustivel', 'observacoes',
        ]
        widgets = {
            'trajeto': forms.Select(attrs={'class': 'form-select'}),
            'veiculo': forms.Select(attrs={'class': 'form-select'}),
            'agendamento': forms.Select(attrs={'class': 'form-select'}),
            'local_posto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome ou endereço do posto',
            }),
            'data_hora': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'km_atual': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 45200',
            }),
            'litros_abastecidos': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 40.5',
                'step': '0.01',
            }),
            'valor_gasto': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 200.00',
                'step': '0.01',
            }),
            'tipo_combustivel': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
        }
        error_messages = {
            'local_posto': {'required': 'Informe o nome ou endereço do posto.'},
            'data_hora': {
                'required': 'Informe a data e hora do abastecimento.',
                'invalid': _INVALID_DATETIME,
            },
            'km_atual': {
                'required': 'Informe o hodômetro no momento do abastecimento.',
                'invalid': _INVALID_NUMBER,
            },
            'litros_abastecidos': {
                'required': 'Informe a quantidade de litros abastecidos.',
                'invalid': _INVALID_NUMBER,
            },
            'valor_gasto': {
                'required': 'Informe o valor pago no abastecimento.',
                'invalid': _INVALID_NUMBER,
            },
            'tipo_combustivel': {
                'required': 'Selecione o tipo de combustível.',
                'invalid_choice': _INVALID_CHOICE,
            },
        }

    def __init__(self, *args, motorista=None, is_admin=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['trajeto'].required = False
        self.fields['trajeto'].empty_label = '— Selecione um trajeto atribuído —'
        self.fields['veiculo'].required = False
        self.fields['veiculo'].queryset = Veiculo.objects.filter(ativo=True)
        self.fields['agendamento'].required = False
        self.fields['agendamento'].empty_label = '— Sem agendamento vinculado —'

        qs_agendamento = (
            Agendamento.objects
            .filter(status='aprovado')
            .select_related('curso', 'veiculo')
            .order_by('-data_inicio')
        )
        if motorista and not is_admin:
            self.fields['trajeto'].queryset = (
                Trajeto.objects
                .filter(motorista=motorista)
                .select_related('agendamento__veiculo', 'agendamento__curso')
                .order_by('-data_saida')
            )
        else:
            self.fields['trajeto'].queryset = (
                Trajeto.objects
                .select_related('agendamento__veiculo', 'agendamento__curso')
                .order_by('-data_saida')
            )
        self.fields['agendamento'].queryset = qs_agendamento

    def clean_litros_abastecidos(self):
        litros = self.cleaned_data.get('litros_abastecidos')
        if litros is not None and litros <= 0:
            raise forms.ValidationError(
                'A quantidade de litros deve ser maior que zero.'
            )
        return litros

    def clean_valor_gasto(self):
        valor = self.cleaned_data.get('valor_gasto')
        if valor is not None and valor <= 0:
            raise forms.ValidationError(
                'O valor pago deve ser maior que zero.'
            )
        return valor

    def clean_km_atual(self):
        km = self.cleaned_data.get('km_atual')
        if km is not None and km <= 0:
            raise forms.ValidationError(
                'O hodômetro deve ser maior que zero.'
            )
        return km

    def clean_data_hora(self):
        dt = self.cleaned_data.get('data_hora')
        if dt and dt > timezone.now():
            raise forms.ValidationError(
                'A data do abastecimento não pode ser no futuro.'
            )
        return dt

    def clean(self):
        cleaned = super().clean()
        trajeto = cleaned.get('trajeto')
        if trajeto:
            cleaned['veiculo'] = trajeto.agendamento.veiculo
            cleaned['agendamento'] = trajeto.agendamento
        return cleaned


class DeslocamentoForm(forms.ModelForm):
    class Meta:
        model = Deslocamento
        fields = [
            'veiculo', 'origem', 'destino',
            'data_hora_saida', 'data_hora_chegada',
            'km_saida', 'km_chegada', 'observacoes',
        ]
        widgets = {
            'veiculo': forms.Select(attrs={'class': 'form-select'}),
            'origem': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Local de partida (opcional)',
            }),
            'destino': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Local de destino',
            }),
            'data_hora_saida': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'data_hora_chegada': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'km_saida': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 45200',
            }),
            'km_chegada': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 45380',
            }),
            'observacoes': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
        }
        error_messages = {
            'veiculo': {
                'required': 'Selecione o veículo utilizado.',
                'invalid_choice': _INVALID_CHOICE,
            },
            'destino': {'required': 'Informe o local de destino.'},
            'data_hora_saida': {
                'required': 'Informe a data e hora de saída.',
                'invalid': _INVALID_DATETIME,
            },
            'data_hora_chegada': {'invalid': _INVALID_DATETIME},
            'km_saida': {
                'required': 'Informe o hodômetro na saída.',
                'invalid': _INVALID_NUMBER,
            },
            'km_chegada': {'invalid': _INVALID_NUMBER},
        }

    def __init__(self, *args, motorista=None, is_admin=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['veiculo'].queryset = Veiculo.objects.filter(ativo=True)
        self.fields['veiculo'].empty_label = '— Selecione o veículo —'
        self.fields['veiculo'].required = True
        self.fields['origem'].required = False
        self.fields['data_hora_chegada'].required = False
        self.fields['km_chegada'].required = False
        self.fields['observacoes'].required = False

    def clean_km_saida(self):
        km = self.cleaned_data.get('km_saida')
        if km is not None and km <= 0:
            raise forms.ValidationError(
                'O hodômetro de saída deve ser maior que zero.'
            )
        return km

    def clean(self):
        cleaned = super().clean()
        km_saida = cleaned.get('km_saida')
        km_chegada = cleaned.get('km_chegada')
        saida = cleaned.get('data_hora_saida')
        chegada = cleaned.get('data_hora_chegada')

        if km_chegada is not None and km_saida is not None:
            if km_chegada < km_saida:
                self.add_error(
                    'km_chegada',
                    f'Km de chegada ({km_chegada}) não pode ser menor que o '
                    f'de saída ({km_saida}).',
                )
            elif km_chegada == km_saida:
                self.add_error(
                    'km_chegada',
                    'Km de chegada igual ao de saída — verifique os valores.',
                )

        if chegada and saida:
            if chegada < saida:
                self.add_error(
                    'data_hora_chegada',
                    'A chegada não pode ser anterior à saída '
                    f'({saida.strftime("%d/%m/%Y %H:%M")}).',
                )
            elif chegada == saida:
                self.add_error(
                    'data_hora_chegada',
                    'A data/hora de chegada é igual à de saída — verifique.',
                )

        return cleaned


class OcorrenciaForm(forms.ModelForm):
    class Meta:
        model = Ocorrencia
        fields = [
            'trajeto',
            'agendamento', 'tipo', 'gravidade', 'data_hora',
            'local', 'descricao', 'providencias_tomadas', 'numero_boletim',
        ]
        widgets = {
            'trajeto': forms.Select(attrs={'class': 'form-select'}),
            'agendamento': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'gravidade': forms.Select(attrs={'class': 'form-select'}),
            'data_hora': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'local': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Local onde ocorreu',
            }),
            'descricao': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4}
            ),
            'providencias_tomadas': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'numero_boletim': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional',
            }),
        }
        error_messages = {
            'tipo': {
                'required': 'Selecione o tipo de ocorrência.',
                'invalid_choice': _INVALID_CHOICE,
            },
            'gravidade': {
                'required': 'Selecione a gravidade da ocorrência.',
                'invalid_choice': _INVALID_CHOICE,
            },
            'data_hora': {
                'required': 'Informe a data e hora da ocorrência.',
                'invalid': _INVALID_DATETIME,
            },
            'local': {'required': 'Informe o local onde a ocorrência aconteceu.'},
            'descricao': {
                'required': 'Descreva o que aconteceu na ocorrência.',
            },
        }

    def __init__(self, *args, motorista=None, is_admin=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['trajeto'].required = False
        self.fields['trajeto'].empty_label = '— Selecione um trajeto atribuído —'
        self.fields['agendamento'].required = False
        self.fields['agendamento'].empty_label = '— Sem agendamento vinculado —'
        self.fields['providencias_tomadas'].required = False
        self.fields['numero_boletim'].required = False

        qs_agendamento = (
            Agendamento.objects
            .filter(status='aprovado')
            .select_related('curso', 'veiculo')
            .order_by('-data_inicio')
        )
        if motorista and not is_admin:
            self.fields['trajeto'].queryset = (
                Trajeto.objects
                .filter(motorista=motorista)
                .select_related('agendamento__veiculo', 'agendamento__curso')
                .order_by('-data_saida')
            )
        else:
            self.fields['trajeto'].queryset = (
                Trajeto.objects
                .select_related('agendamento__veiculo', 'agendamento__curso')
                .order_by('-data_saida')
            )
        self.fields['agendamento'].queryset = qs_agendamento

    def clean_descricao(self):
        descricao = self.cleaned_data.get('descricao', '').strip()
        if descricao and len(descricao) < 20:
            raise forms.ValidationError(
                'Descreva a ocorrência com mais detalhes (mínimo 20 caracteres).'
            )
        return descricao

    def clean_data_hora(self):
        dt = self.cleaned_data.get('data_hora')
        if dt and dt > timezone.now():
            raise forms.ValidationError(
                'A data da ocorrência não pode ser no futuro.'
            )
        return dt

    def clean(self):
        cleaned = super().clean()
        trajeto = cleaned.get('trajeto')
        if trajeto:
            cleaned['agendamento'] = trajeto.agendamento
        return cleaned
