from django import forms

from agendamentos.models import Agendamento
from veiculos.models import Veiculo

from .models import Abastecimento, Ocorrencia


class AbastecimentoForm(forms.ModelForm):
    class Meta:
        model = Abastecimento
        fields = [
            'veiculo', 'agendamento', 'local_posto', 'data_hora',
            'km_atual', 'litros_abastecidos', 'valor_gasto',
            'tipo_combustivel', 'observacoes',
        ]
        widgets = {
            'veiculo': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'agendamento': forms.Select(
                attrs={'class': 'form-select'}
            ),
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
            'tipo_combustivel': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'observacoes': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
        }

    def __init__(self, *args, motorista=None, is_admin=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['veiculo'].queryset = Veiculo.objects.filter(ativo=True)
        self.fields['agendamento'].required = False
        self.fields['agendamento'].empty_label = (
            '— Sem agendamento vinculado —'
        )
        if motorista and not is_admin:
            self.fields['agendamento'].queryset = (
                Agendamento.objects
                .filter(professor=motorista, status='aprovado')
                .select_related('curso', 'veiculo')
                .order_by('-data_inicio')
            )
        else:
            self.fields['agendamento'].queryset = (
                Agendamento.objects
                .filter(status='aprovado')
                .select_related('curso', 'veiculo')
                .order_by('-data_inicio')
            )


class OcorrenciaForm(forms.ModelForm):
    class Meta:
        model = Ocorrencia
        fields = [
            'agendamento', 'tipo', 'gravidade', 'data_hora',
            'local', 'descricao', 'providencias_tomadas', 'numero_boletim',
        ]
        widgets = {
            'agendamento': forms.Select(
                attrs={'class': 'form-select'}
            ),
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

    def __init__(self, *args, motorista=None, is_admin=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['providencias_tomadas'].required = False
        self.fields['numero_boletim'].required = False

        if motorista and not is_admin:
            self.fields['agendamento'].queryset = (
                Agendamento.objects
                .filter(professor=motorista)
                .select_related('curso', 'veiculo')
                .order_by('-data_inicio')
            )
        else:
            self.fields['agendamento'].queryset = (
                Agendamento.objects
                .filter(status='aprovado')
                .select_related('curso', 'veiculo')
                .order_by('-data_inicio')
            )
