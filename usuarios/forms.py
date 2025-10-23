from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import Usuario

# Perguntas padrão disponíveis
PERGUNTAS_SEGURANCA = [
    ('cidade_nascimento', 'Em qual cidade você nasceu?'),
    ('nome_mae', 'Qual o nome de solteira da sua mãe?'),
    ('animal_estimacao', 'Qual o nome do seu primeiro animal de estimação?'),
    ('escola', 'Qual o nome da sua primeira escola?'),
    ('comida_favorita', 'Qual sua comida favorita?'),
    ('time', 'Qual seu time de futebol?'),
    ('livro_favorito', 'Qual seu livro favorito?'),
    ('professor_favorito', 'Qual o nome do seu professor favorito?'),
]


class RegistroForm(UserCreationForm):
    """Formulário de registro para professores"""
    email = forms.EmailField(required=True, label='E-mail')
    first_name = forms.CharField(required=True, label='Nome')
    last_name = forms.CharField(required=True, label='Sobrenome')
    telefone = forms.CharField(required=False, label='Telefone')

    # Perguntas de segurança
    pergunta_seguranca_1 = forms.ChoiceField(
        label='Pergunta de Segurança 1',
        choices=PERGUNTAS_SEGURANCA,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    resposta_seguranca_1 = forms.CharField(
        label='Resposta 1',
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua resposta'
        })
    )
    pergunta_seguranca_2 = forms.ChoiceField(
        label='Pergunta de Segurança 2',
        choices=PERGUNTAS_SEGURANCA,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    resposta_seguranca_2 = forms.CharField(
        label='Resposta 2',
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua resposta'
        })
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'first_name', 'last_name', 'telefone',
            'password1', 'password2',
            'pergunta_seguranca_1', 'resposta_seguranca_1',
            'pergunta_seguranca_2', 'resposta_seguranca_2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona classes Bootstrap aos campos
        for field_name, field in self.fields.items():
            if field_name not in ['pergunta_seguranca_1',
                                  'pergunta_seguranca_2']:
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'

            if field_name == 'username':
                field.help_text = (
                    'Obrigatório. 150 caracteres ou menos. '
                    'Letras, dígitos e @/./+/-/_ apenas.'
                )
            elif field_name == 'password1':
                field.help_text = (
                    'Sua senha deve conter pelo menos 8 caracteres.'
                )
            elif field_name == 'password2':
                field.help_text = (
                    'Digite a mesma senha novamente para verificação.'
                )
            elif field_name == 'telefone':
                field.widget.attrs['placeholder'] = '(00) 00000-0000'
                field.help_text = 'Formato: (XX) XXXXX-XXXX'

    def clean_username(self):
        """Converte username para minúsculas e valida unicidade"""
        username = self.cleaned_data.get('username')
        if username:
            username = username.lower()
            # Verifica se já existe (exceto o próprio usuário em edição)
            if Usuario.objects.filter(username=username).exists():
                raise forms.ValidationError(
                    'Este nome de usuário já está em uso.'
                )
            return username
        return username

    def clean_email(self):
        """
        Valida email institucional da UESPI e verifica unicidade
        """
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            # Aceita emails que terminam com @*.uespi.br
            # Exemplos: @uespi.br, @aluno.uespi.br, @professor.uespi.br
            if not (email.endswith('.uespi.br') or
                        email.endswith('@uespi.br')):
                 raise forms.ValidationError(
                    'Por favor, utilize um e-mail institucional da UESPI '
                     '(@uespi.br ou @*.uespi.br). '
                     'Exemplo: nome@professor.uespi.br'
                )
            # Verifica se já existe (exceto o próprio usuário em edição)
            if Usuario.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    'Este e-mail já está cadastrado.'
                )
            return email
        return email

    def clean_telefone(self):
        """Remove formatação do telefone antes de salvar"""
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            # Remove todos os caracteres que não são dígitos
            telefone = ''.join(filter(str.isdigit, telefone))
        return telefone

    def clean(self):
        cleaned_data = super().clean()
        pergunta_1 = cleaned_data.get('pergunta_seguranca_1')
        pergunta_2 = cleaned_data.get('pergunta_seguranca_2')

        if pergunta_1 and pergunta_2 and pergunta_1 == pergunta_2:
            raise forms.ValidationError(
                'Por favor, escolha perguntas diferentes.'
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo_usuario = 'professor'  # Define como professor por padrão
        if commit:
            user.save()
        return user


class RecuperarSenhaStep1Form(forms.Form):
    """Formulário para informar o username ou email"""
    username = forms.CharField(
        label='Usuário ou E-mail',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu usuário ou e-mail'
        })
    )

    def clean_username(self):
        """Converte para minúsculas"""
        username = self.cleaned_data.get('username')
        if username:
            return username.lower()
        return username


class RecuperarSenhaStep2Form(forms.Form):
    """Formulário para responder perguntas de segurança"""
    resposta_1 = forms.CharField(
        label='',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua resposta'
        })
    )
    resposta_2 = forms.CharField(
        label='',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua resposta'
        })
    )


class RecuperarSenhaStep3Form(forms.Form):
    """Formulário para definir nova senha"""
    nova_senha = forms.CharField(
        label='Nova Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua nova senha'
        }),
        min_length=8,
        help_text='Sua senha deve conter pelo menos 8 caracteres.'
    )
    confirmar_senha = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite novamente sua nova senha'
        }),
        min_length=8
    )

    def clean(self):
        cleaned_data = super().clean()
        nova_senha = cleaned_data.get('nova_senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')

        if nova_senha and confirmar_senha:
            if nova_senha != confirmar_senha:
                raise forms.ValidationError('As senhas não conferem.')

        return cleaned_data


class ConfigurarPerguntasSegurancaForm(forms.ModelForm):
    """Formulário para configurar perguntas de segurança"""
    pergunta_seguranca_1 = forms.ChoiceField(
        label='Pergunta de Segurança 1',
        choices=PERGUNTAS_SEGURANCA,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    resposta_seguranca_1 = forms.CharField(
        label='Resposta 1',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua resposta'
        })
    )
    pergunta_seguranca_2 = forms.ChoiceField(
        label='Pergunta de Segurança 2',
        choices=PERGUNTAS_SEGURANCA,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    resposta_seguranca_2 = forms.CharField(
        label='Resposta 2',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua resposta'
        })
    )

    class Meta:
        model = Usuario
        fields = [
            'pergunta_seguranca_1',
            'resposta_seguranca_1',
            'pergunta_seguranca_2',
            'resposta_seguranca_2'
        ]

    def clean(self):
        cleaned_data = super().clean()
        pergunta_1 = cleaned_data.get('pergunta_seguranca_1')
        pergunta_2 = cleaned_data.get('pergunta_seguranca_2')

        if pergunta_1 and pergunta_2 and pergunta_1 == pergunta_2:
            raise forms.ValidationError(
                'Por favor, escolha perguntas diferentes.'
            )

        return cleaned_data


class EditarPerfilForm(forms.ModelForm):
    """Formulário para editar perfil do usuário"""
    first_name = forms.CharField(
        label='Nome',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Sobrenome',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='E-mail',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    telefone = forms.CharField(
        label='Telefone',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(00) 00000-0000'
        }),
        help_text='Formato: (XX) XXXXX-XXXX'
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefone']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Formata o telefone ao carregar para exibição
        if self.instance and self.instance.telefone:
            telefone = self.instance.telefone
            # Remove formatação existente
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            
            # Aplica formatação
            if len(telefone_limpo) == 11:
                # (XX) XXXXX-XXXX
                self.initial['telefone'] = (
                    f'({telefone_limpo[:2]}) '
                    f'{telefone_limpo[2:7]}-{telefone_limpo[7:]}'
                )
            elif len(telefone_limpo) == 10:
                # (XX) XXXX-XXXX
                self.initial['telefone'] = (
                    f'({telefone_limpo[:2]}) '
                    f'{telefone_limpo[2:6]}-{telefone_limpo[6:]}'
                )

    def clean_email(self):
        """Valida se o e-mail já existe (exceto o próprio usuário)"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            # Verifica se já existe outro usuário com este e-mail
            qs = Usuario.objects.filter(email=email)
            if self.user:
                qs = qs.exclude(pk=self.user.pk)
            if qs.exists():
                raise forms.ValidationError('Este e-mail já está cadastrado.')
            return email
        return email

    def clean_telefone(self):
        """Remove formatação do telefone antes de salvar"""
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            # Remove todos os caracteres que não são dígitos
            telefone = ''.join(filter(str.isdigit, telefone))
        return telefone


class AlterarSenhaForm(forms.Form):
    """Formulário para alterar senha"""
    senha_atual = forms.CharField(
        label='Senha Atual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha atual'
        })
    )
    nova_senha = forms.CharField(
        label='Nova Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua nova senha'
        }),
        min_length=8,
        help_text=(
            'Sua senha deve conter pelo menos 8 caracteres e não pode ser '
            'muito comum ou inteiramente numérica.'
        )
    )
    confirmar_senha = forms.CharField(
        label='Confirmar Nova Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite novamente sua nova senha'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_senha_atual(self):
        """Valida se a senha atual está correta"""
        senha_atual = self.cleaned_data.get('senha_atual')
        if self.user and not self.user.check_password(senha_atual):
            raise forms.ValidationError('Senha atual incorreta.')
        return senha_atual

    def clean_nova_senha(self):
        """Valida a força da nova senha"""
        nova_senha = self.cleaned_data.get('nova_senha')
        if nova_senha and self.user:
            try:
                # Usa os validadores de senha do Django
                validate_password(nova_senha, self.user)
            except DjangoValidationError as e:
                raise forms.ValidationError(e.messages)
        return nova_senha

    def clean(self):
        cleaned_data = super().clean()
        nova_senha = cleaned_data.get('nova_senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')

        if nova_senha and confirmar_senha:
            if nova_senha != confirmar_senha:
                raise forms.ValidationError('As novas senhas não conferem.')

        return cleaned_data
