from django import forms
from .models import Veiculo


class VeiculoForm(forms.ModelForm):
    """Formulário para criar/editar veículos"""
    
    class Meta:
        model = Veiculo
        fields = ['placa', 'modelo', 'marca', 'ano', 'cor', 'capacidade_passageiros', 'observacoes', 'ativo']
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ABC-1234'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control'}),
            'cor': forms.TextInput(attrs={'class': 'form-control'}),
            'capacidade_passageiros': forms.NumberInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
