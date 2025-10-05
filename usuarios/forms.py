from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class RegistroForm(UserCreationForm):
    """Formulário de registro para professores"""
    email = forms.EmailField(required=True, label='E-mail')
    first_name = forms.CharField(required=True, label='Nome')
    last_name = forms.CharField(required=True, label='Sobrenome')
    telefone = forms.CharField(required=False, label='Telefone')
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'telefone', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona classes Bootstrap aos campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'username':
                field.help_text = 'Obrigatório. 150 caracteres ou menos. Letras, dígitos e @/./+/-/_ apenas.'
            elif field_name == 'password1':
                field.help_text = 'Sua senha deve conter pelo menos 8 caracteres.'
            elif field_name == 'password2':
                field.help_text = 'Digite a mesma senha novamente para verificação.'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo_usuario = 'professor'  # Define como professor por padrão
        if commit:
            user.save()
        return user
