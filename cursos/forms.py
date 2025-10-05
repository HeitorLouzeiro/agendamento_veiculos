from django import forms
from .models import Curso


class CursoForm(forms.ModelForm):
    """Formulário para criar/editar cursos"""
    
    class Meta:
        model = Curso
        fields = ['nome', 'limite_km_mensal', 'descricao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'limite_km_mensal': forms.NumberInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
