from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import Agendamento, Trajeto
from cursos.models import Curso
from veiculos.models import Veiculo


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
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Filtra apenas cursos e veículos ativos
        self.fields['curso'].queryset = Curso.objects.filter(ativo=True)
        self.fields['veiculo'].queryset = Veiculo.objects.filter(ativo=True)
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        veiculo = cleaned_data.get('veiculo')
        
        # Validação de datas
        if data_inicio and data_fim and data_fim <= data_inicio:
            raise ValidationError({
                'data_fim': 'A data de fim deve ser posterior à data de início.'
            })
        
        # Validação de conflito de veículo
        if veiculo and data_inicio and data_fim:
            agendamento_id = self.instance.id if self.instance else None
            if veiculo.tem_conflito(data_inicio, data_fim, agendamento_id):
                conflitos = veiculo.get_agendamentos_periodo(data_inicio, data_fim)
                if agendamento_id:
                    conflitos = conflitos.exclude(id=agendamento_id)
                
                mensagem = f"O veículo {veiculo.placa} já está agendado neste período:"
                for conflito in conflitos:
                    mensagem += f"\n- {conflito.data_inicio.strftime('%d/%m/%Y %H:%M')} até {conflito.data_fim.strftime('%d/%m/%Y %H:%M')} ({conflito.curso.nome})"
                
                raise ValidationError({
                    'veiculo': mensagem
                })
        
        return cleaned_data


class TrajetoForm(forms.ModelForm):
    """Formulário para trajetos"""
    
    class Meta:
        model = Trajeto
        fields = ['origem', 'destino', 'data_saida', 'data_chegada', 'quilometragem', 'descricao']
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
            'quilometragem': forms.NumberInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


# Formset para trajetos inline
TrajetoFormSet = inlineformset_factory(
    Agendamento,
    Trajeto,
    form=TrajetoForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)
