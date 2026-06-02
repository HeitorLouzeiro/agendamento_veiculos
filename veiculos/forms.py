from django import forms

from campus.models import Campus

from .models import Veiculo


class VeiculoForm(forms.ModelForm):
    """Formulário para criar/editar veículos"""

    class Meta:
        model = Veiculo
        fields = [
            'campus', 'placa', 'modelo', 'marca', 'ano', 'cor',
            'capacidade_passageiros', 'observacoes', 'ativo',
        ]
        widgets = {
            'campus': forms.Select(attrs={'class': 'form-select'}),
            'placa': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'ABC-1234'}
            ),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control'}),
            'cor': forms.TextInput(attrs={'class': 'form-control'}),
            'capacidade_passageiros': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),
            'observacoes': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'ativo': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }

    def __init__(self, *args, campus_fixo=None, **kwargs):
        super().__init__(*args, **kwargs)
        if campus_fixo:
            self.fields['campus'].queryset = Campus.objects.filter(
                pk=campus_fixo.pk
            )
            self.fields['campus'].initial = campus_fixo
            self.fields['campus'].widget.attrs['disabled'] = True
            self.fields['campus'].required = False
        else:
            self.fields['campus'].queryset = Campus.objects.filter(
                ativo=True
            )
            self.fields['campus'].required = True
            self.fields['campus'].empty_label = (
                '— Selecione ou digite o nome do campus —'
            )
            self.fields['campus'].widget.attrs['class'] = (
                'form-select select2-campus'
            )
