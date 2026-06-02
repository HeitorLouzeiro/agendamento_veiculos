from django import forms

from .models import Campus


class CampusForm(forms.ModelForm):
    class Meta:
        model = Campus
        fields = ['nome', 'cidade', 'endereco', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
