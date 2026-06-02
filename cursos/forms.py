from django import forms

from campus.models import Campus

from .models import Curso


class CursoForm(forms.ModelForm):
    """Formulário para criar/editar cursos"""

    class Meta:
        model = Curso
        fields = ['nome', 'campus', 'limite_km_mensal', 'descricao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'campus': forms.Select(attrs={'class': 'form-select'}),
            'limite_km_mensal': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),
            'descricao': forms.Textarea(
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
