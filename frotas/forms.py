from django import forms

from agendamentos.models import Agendamento, Trajeto
from veiculos.models import Veiculo

from .models import Abastecimento, Deslocamento, Ocorrencia


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
            'trajeto',
            'veiculo', 'agendamento', 'origem', 'destino',
            'data_hora_saida', 'data_hora_chegada',
            'km_saida', 'km_chegada', 'observacoes',
        ]
        widgets = {
            'trajeto': forms.Select(attrs={'class': 'form-select'}),
            'veiculo': forms.Select(attrs={'class': 'form-select'}),
            'agendamento': forms.Select(attrs={'class': 'form-select'}),
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

    def __init__(self, *args, motorista=None, is_admin=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_admin = is_admin

        # Campos sempre opcionais
        self.fields['trajeto'].required = False
        self.fields['trajeto'].empty_label = '— Selecione um trajeto atribuído —'
        self.fields['agendamento'].required = False
        self.fields['agendamento'].empty_label = '— Sem agendamento vinculado —'
        self.fields['veiculo'].required = False
        self.fields['origem'].required = False
        self.fields['data_hora_chegada'].required = False
        self.fields['km_chegada'].required = False
        self.fields['observacoes'].required = False

        if motorista and not is_admin:
            # Motorista vê apenas os trajetos atribuídos a si
            self.fields['trajeto'].queryset = (
                Trajeto.objects
                .filter(motorista=motorista)
                .select_related('agendamento__veiculo', 'agendamento__curso')
                .order_by('-data_saida')
            )
            # Veículo e agendamento ficam livres (preenchidos via JS/server)
            self.fields['veiculo'].queryset = Veiculo.objects.filter(ativo=True)
            self.fields['agendamento'].queryset = (
                Agendamento.objects
                .filter(status='aprovado')
                .select_related('curso', 'veiculo')
                .order_by('-data_inicio')
            )
        else:
            # Admin vê todos os trajetos
            self.fields['trajeto'].queryset = (
                Trajeto.objects
                .select_related('agendamento__veiculo', 'agendamento__curso')
                .order_by('-data_saida')
            )
            self.fields['veiculo'].queryset = Veiculo.objects.filter(ativo=True)
            self.fields['agendamento'].queryset = (
                Agendamento.objects
                .filter(status='aprovado')
                .select_related('curso', 'veiculo')
                .order_by('-data_inicio')
            )

    def clean(self):
        cleaned = super().clean()
        trajeto = cleaned.get('trajeto')

        # Se trajeto selecionado, herda veiculo e agendamento dele
        if trajeto:
            cleaned['veiculo'] = trajeto.agendamento.veiculo
            cleaned['agendamento'] = trajeto.agendamento
            if not cleaned.get('destino'):
                cleaned['destino'] = trajeto.destino
            if not cleaned.get('origem'):
                cleaned['origem'] = trajeto.origem

        # Valida que tem destino (obrigatório no model)
        if not cleaned.get('destino'):
            self.add_error('destino', 'Informe o destino.')

        km_saida = cleaned.get('km_saida')
        km_chegada = cleaned.get('km_chegada')
        saida = cleaned.get('data_hora_saida')
        chegada = cleaned.get('data_hora_chegada')
        if km_chegada is not None and km_saida is not None:
            if km_chegada < km_saida:
                self.add_error(
                    'km_chegada',
                    'Km na chegada não pode ser menor que o km na saída.',
                )
        if chegada and saida and chegada < saida:
            self.add_error(
                'data_hora_chegada',
                'Data/hora de chegada não pode ser anterior à saída.',
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

    def clean(self):
        cleaned = super().clean()
        trajeto = cleaned.get('trajeto')
        if trajeto:
            cleaned['agendamento'] = trajeto.agendamento
        return cleaned
