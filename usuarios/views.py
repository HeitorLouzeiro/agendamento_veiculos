from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from common.decorators import responsavel_campus_required
from common.pagination import PaginationHelper

from .forms import (PERGUNTAS_SEGURANCA, AlterarSenhaForm,
                    CriarMotoristaForm, CriarProfessorForm,
                    EditarPerfilForm, RecuperarSenhaStep1Form,
                    RecuperarSenhaStep2Form, RecuperarSenhaStep3Form,
                    RegistroForm)
from .models import Usuario


class CustomLoginView(LoginView):
    """View customizada de login"""
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_motorista():
            return reverse('frotas:dashboard_motorista')
        if user.is_responsavel_campus():
            return reverse('frotas:dashboard_responsavel')
        return '/'

    def form_valid(self, form):
        """Converte username para minúsculas antes de validar"""
        username = form.cleaned_data.get('username')
        if username:
            form.cleaned_data['username'] = username.lower()
        return super().form_valid(form)

    def form_invalid(self, form):
        """Verifica se o usuário existe mas está inativo"""
        username = self.request.POST.get('username', '').lower()
        password = self.request.POST.get('password', '')

        if username and password:
            try:
                # Busca por username ou email
                usuario = Usuario.objects.get(
                    Q(username=username) | Q(email__iexact=username)
                )

                # Verifica se a senha está correta e o usuário inativo
                if usuario.check_password(password) and not usuario.is_active:
                    messages.error(
                        self.request,
                        'Sua conta ainda não foi ativada. '
                        'Por favor, verifique seu e-mail e clique no link '
                        'de ativação enviado para você. '
                        'Se não recebeu o e-mail, '
                        '<a href="/usuarios/reenviar-ativacao/" '
                        'class="alert-link">clique aqui para reenviar</a>.',
                        extra_tags='safe'
                    )
                    return self.render_to_response(
                        self.get_context_data(form=form)
                    )
            except Usuario.DoesNotExist:
                pass
            except Usuario.MultipleObjectsReturned:
                pass

        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """View customizada de logout"""
    next_page = 'usuarios:login'


def registro(request):
    """View para registro de novos professores"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.gerar_token_ativacao()
            user.save()
            grupo, _ = Group.objects.get_or_create(name='Professores')
            user.groups.add(grupo)

            # Envia email de ativação
            try:
                link_ativacao = request.build_absolute_uri(
                    reverse('usuarios:ativar_conta',
                            args=[user.token_ativacao])
                )

                assunto = 'Ative sua conta - Sistema de Agendamento UESPI'
                mensagem = (
                    f'Olá, {user.get_full_name()}!\n\n'
                    f'Obrigado por se registrar no Sistema de Agendamento '
                    f'de Veículos da UESPI.\n\n'
                    f'Para ativar sua conta, clique no link abaixo:\n'
                    f'{link_ativacao}\n\n'
                    f'Este link é válido por 24 horas.\n\n'
                    f'Se você não se cadastrou, ignore este e-mail.\n\n'
                    f'Atenciosamente,\n'
                    f'Equipe Sistema de Agendamento - UESPI'
                )

                send_mail(
                    assunto,
                    mensagem,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

                messages.success(
                    request,
                    f'Cadastro realizado com sucesso! '
                    f'Um e-mail de ativação foi enviado para {user.email}. '
                    f'Por favor, verifique sua caixa de entrada e spam.'
                )
            except Exception as e:
                # Se falhar envio de email, avisa usuário
                messages.warning(
                    request,
                    f'Cadastro realizado, mas houve um erro ao enviar '
                    f'o e-mail de ativação. Entre em contato com o '
                    f'administrador. Erro: {str(e)}'
                )

            return redirect('usuarios:login')
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {'form': form})


def confirmar_email(request, token):
    """View para ativar conta através do token"""
    try:
        usuario = Usuario.objects.get(token_ativacao=token)

        # Verifica se o token não expirou (24 horas)
        if usuario.token_criado_em:
            tempo_decorrido = timezone.now() - usuario.token_criado_em
            if tempo_decorrido.total_seconds() > 86400:  # 24 horas
                messages.error(
                    request,
                    'Este link de ativação expirou. '
                    'Por favor, solicite um novo link.'
                )
                return redirect('usuarios:login')

        # Ativa a conta
        usuario.is_active = True
        usuario.token_ativacao = ''  # Limpa o token usado
        usuario.save()

        messages.success(
            request,
            f'Conta ativada com sucesso! '
            f'Bem-vindo, {usuario.get_full_name()}. '
            f'Agora você pode fazer login no sistema.'
        )
        return redirect('usuarios:login')

    except Usuario.DoesNotExist:
        messages.error(
            request,
            'Link de ativação inválido. '
            'Verifique o link e tente novamente.'
        )
        return redirect('usuarios:login')


def reenviar_email_confirmacao(request):
    """View para reenviar email de ativação"""
    if request.method == 'POST':
        email = request.POST.get('email', '').lower()

        try:
            usuario = Usuario.objects.get(email=email, is_active=False)

            # Gera novo token
            usuario.gerar_token_ativacao()
            usuario.save()

            # Envia email
            try:
                link_ativacao = request.build_absolute_uri(
                    reverse('usuarios:ativar_conta',
                            args=[usuario.token_ativacao])
                )

                assunto = 'Ative sua conta - Sistema de Agendamento UESPI'
                mensagem = (
                    f'Olá, {usuario.get_full_name()}!\n\n'
                    f'Você solicitou um novo link de ativação.\n\n'
                    f'Para ativar sua conta, clique no link abaixo:\n'
                    f'{link_ativacao}\n\n'
                    f'Este link é válido por 24 horas.\n\n'
                    f'Atenciosamente,\n'
                    f'Equipe Sistema de Agendamento - UESPI'
                )

                send_mail(
                    assunto,
                    mensagem,
                    settings.DEFAULT_FROM_EMAIL,
                    [usuario.email],
                    fail_silently=False,
                )

                messages.success(
                    request,
                    f'Um novo e-mail de ativação foi enviado para '
                    f'{usuario.email}.'
                )
            except Exception as e:
                messages.error(
                    request,
                    f'Erro ao enviar e-mail: {str(e)}'
                )
        except Usuario.DoesNotExist:
            # Por segurança, não informa se o email existe ou não
            messages.info(
                request,
                'Se o e-mail informado estiver cadastrado e pendente de '
                'ativação, você receberá um novo link.'
            )

        return redirect('usuarios:login')

    return render(request, 'usuarios/reenviar_confirmacao.html')


def recuperar_senha_step1(request):
    """Passo 1: Informar username ou email"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RecuperarSenhaStep1Form(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            try:
                # Busca por username ou email
                usuario = Usuario.objects.get(
                    Q(username=username_or_email) |
                    Q(email__iexact=username_or_email)
                )

                # Verifica se o usuário configurou perguntas
                if not usuario.pergunta_seguranca_1 or \
                   not usuario.pergunta_seguranca_2:
                    messages.error(
                        request,
                        'Este usuário não possui perguntas de segurança '
                        'configuradas. Entre em contato com o administrador.'
                    )
                    return redirect('usuarios:recuperar_senha_step1')

                # Salva username real na sessão (não o email)
                request.session['recuperar_username'] = usuario.username
                return redirect('usuarios:recuperar_senha_step2')
            except Usuario.DoesNotExist:
                messages.error(
                    request,
                    'Usuário ou e-mail não encontrado.'
                )
            except Usuario.MultipleObjectsReturned:
                messages.error(
                    request,
                    'Erro ao localizar usuário. '
                    'Entre em contato com o administrador.'
                )
    else:
        form = RecuperarSenhaStep1Form()

    return render(
        request,
        'usuarios/recuperar_senha_step1.html',
        {'form': form}
    )


def recuperar_senha_step2(request):
    """Passo 2: Responder perguntas de segurança"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    username = request.session.get('recuperar_username')
    if not username:
        messages.error(
            request,
            'Sessão expirada. Por favor, comece novamente.'
        )
        return redirect('usuarios:recuperar_senha_step1')

    try:
        usuario = Usuario.objects.get(username=username)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('recuperar_senha_step1')

    # Busca o texto das perguntas
    perguntas_dict = dict(PERGUNTAS_SEGURANCA)
    pergunta_1_texto = perguntas_dict.get(
        usuario.pergunta_seguranca_1,
        usuario.pergunta_seguranca_1
    )
    pergunta_2_texto = perguntas_dict.get(
        usuario.pergunta_seguranca_2,
        usuario.pergunta_seguranca_2
    )

    if request.method == 'POST':
        form = RecuperarSenhaStep2Form(request.POST)
        if form.is_valid():
            resposta_1 = form.cleaned_data['resposta_1'].strip().lower()
            resposta_2 = form.cleaned_data['resposta_2'].strip().lower()

            # Verifica as respostas
            resposta_correta_1 = usuario.resposta_seguranca_1.strip().lower()
            resposta_correta_2 = usuario.resposta_seguranca_2.strip().lower()

            if resposta_1 == resposta_correta_1 and \
               resposta_2 == resposta_correta_2:
                # Respostas corretas
                request.session['recuperar_verificado'] = True
                return redirect('usuarios:recuperar_senha_step3')
            else:
                messages.error(
                    request,
                    'Respostas incorretas. Tente novamente.'
                )
    else:
        form = RecuperarSenhaStep2Form()

    return render(
        request,
        'usuarios/recuperar_senha_step2.html',
        {
            'form': form,
            'pergunta_1': pergunta_1_texto,
            'pergunta_2': pergunta_2_texto,
        }
    )


def recuperar_senha_step3(request):
    """Passo 3: Definir nova senha"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    username = request.session.get('recuperar_username')
    verificado = request.session.get('recuperar_verificado')

    if not username or not verificado:
        messages.error(
            request,
            'Sessão inválida. Por favor, comece novamente.'
        )
        return redirect('usuarios:recuperar_senha_step1')

    try:
        usuario = Usuario.objects.get(username=username)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('usuarios:recuperar_senha_step1')

    if request.method == 'POST':
        form = RecuperarSenhaStep3Form(request.POST)
        if form.is_valid():
            nova_senha = form.cleaned_data['nova_senha']
            usuario.set_password(nova_senha)
            usuario.save()

            # Limpa a sessão
            request.session.pop('recuperar_username', None)
            request.session.pop('recuperar_verificado', None)

            messages.success(
                request,
                'Senha alterada com sucesso! Você já pode fazer login.'
            )
            return redirect('usuarios:login')
    else:
        form = RecuperarSenhaStep3Form()

    return render(
        request,
        'usuarios/recuperar_senha_step3.html',
        {'form': form}
    )


def editar_perfil(request):
    """View para editar perfil do usuário"""
    if not request.user.is_authenticated:
        return redirect('usuarios:login')

    if request.method == 'POST':
        form = EditarPerfilForm(
            request.POST,
            instance=request.user,
            user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Perfil atualizado com sucesso!'
            )
            return redirect('usuarios:editar_perfil')
    else:
        form = EditarPerfilForm(
            instance=request.user,
            user=request.user
        )

    return render(
        request,
        'usuarios/editar_perfil.html',
        {'form': form}
    )


def alterar_senha(request):
    """View para alterar senha do usuário"""
    if not request.user.is_authenticated:
        return redirect('usuarios:login')

    if request.method == 'POST':
        form = AlterarSenhaForm(request.POST, user=request.user)
        if form.is_valid():
            nova_senha = form.cleaned_data['nova_senha']
            request.user.set_password(nova_senha)
            request.user.save()

            # Faz login novamente para manter sessão ativa
            backend = 'usuarios.backends.EmailOrUsernameBackend'
            request.user.backend = backend
            login(request, request.user, backend=backend)

            messages.success(
                request,
                'Senha alterada com sucesso!'
            )
            return redirect('usuarios:editar_perfil')
    else:
        form = AlterarSenhaForm(user=request.user)

    return render(
        request,
        'usuarios/alterar_senha.html',
        {'form': form}
    )


@login_required
@responsavel_campus_required
def lista_motoristas(request):
    is_admin = request.user.is_administrador()
    if is_admin:
        motoristas = Usuario.objects.filter(
            groups__name='Motoristas',
        ).select_related('campus').order_by(
            'campus__nome', 'first_name', 'last_name'
        )
    else:
        motoristas = Usuario.objects.filter(
            groups__name='Motoristas',
            campus=request.user.campus,
        ).order_by('first_name', 'last_name')
    pagination = PaginationHelper(motoristas, 10)
    motoristas_paginados = pagination.get_page(request.GET.get('page'))
    return render(
        request,
        'usuarios/motoristas_lista.html',
        {'motoristas': motoristas_paginados, 'is_admin': is_admin},
    )


@login_required
@responsavel_campus_required
def criar_motorista(request):
    is_admin = request.user.is_administrador()
    if request.method == 'POST':
        form = CriarMotoristaForm(request.POST, admin_mode=is_admin)
        if form.is_valid():
            motorista = form.save(commit=False)
            if is_admin:
                motorista.campus = form.cleaned_data['campus']
            else:
                motorista.campus = request.user.campus
            motorista.is_active = True
            motorista.save()
            grupo, _ = Group.objects.get_or_create(name='Motoristas')
            motorista.groups.add(grupo)
            messages.success(
                request,
                f'Motorista {motorista.get_full_name()} criado com sucesso!'
            )
            return redirect('usuarios:lista_motoristas')
    else:
        form = CriarMotoristaForm(admin_mode=is_admin)
    return render(
        request,
        'usuarios/motorista_form.html',
        {'form': form, 'titulo': 'Novo Motorista'},
    )


@login_required
@responsavel_campus_required
def editar_motorista(request, uuid):
    is_admin = request.user.is_administrador()
    if is_admin:
        motorista = get_object_or_404(
            Usuario, uuid=uuid, groups__name='Motoristas'
        )
    else:
        motorista = get_object_or_404(
            Usuario, uuid=uuid, groups__name='Motoristas',
            campus=request.user.campus
        )
    if request.method == 'POST':
        form = CriarMotoristaForm(
            request.POST, instance=motorista, admin_mode=is_admin
        )
        if form.is_valid():
            saved = form.save(commit=False)
            if is_admin:
                saved.campus = form.cleaned_data['campus']
            saved.save()
            messages.success(request, 'Motorista atualizado com sucesso!')
            return redirect('usuarios:lista_motoristas')
    else:
        form = CriarMotoristaForm(instance=motorista, admin_mode=is_admin)
    return render(
        request,
        'usuarios/motorista_form.html',
        {'form': form, 'titulo': 'Editar Motorista', 'motorista': motorista},
    )


@login_required
@responsavel_campus_required
def desativar_motorista(request, uuid):
    is_admin = request.user.is_administrador()
    if is_admin:
        motorista = get_object_or_404(
            Usuario, uuid=uuid, groups__name='Motoristas'
        )
    else:
        motorista = get_object_or_404(
            Usuario, uuid=uuid, groups__name='Motoristas',
            campus=request.user.campus
        )
    if request.method == 'POST':
        motorista.is_active = not motorista.is_active
        motorista.save()
        status = 'ativado' if motorista.is_active else 'desativado'
        messages.success(request, f'Motorista {status} com sucesso!')
        return redirect('usuarios:lista_motoristas')
    return render(
        request,
        'usuarios/motorista_desativar.html',
        {'motorista': motorista},
    )


@login_required
@responsavel_campus_required
def lista_professores(request):
    is_admin = request.user.is_administrador()
    if is_admin:
        professores = Usuario.objects.filter(
            groups__name='Professores',
        ).select_related('campus').order_by(
            'campus__nome', 'first_name', 'last_name'
        )
    else:
        professores = Usuario.objects.filter(
            groups__name='Professores',
            campus=request.user.campus,
        ).order_by('first_name', 'last_name')
    pagination = PaginationHelper(professores, 10)
    professores_paginados = pagination.get_page(request.GET.get('page'))
    return render(
        request,
        'usuarios/professores_lista.html',
        {'professores': professores_paginados, 'is_admin': is_admin},
    )


@login_required
@responsavel_campus_required
def criar_professor(request):
    is_admin = request.user.is_administrador()
    if request.method == 'POST':
        form = CriarProfessorForm(request.POST, admin_mode=is_admin)
        if form.is_valid():
            professor = form.save(commit=False)
            if is_admin:
                professor.campus = form.cleaned_data['campus']
            else:
                professor.campus = request.user.campus
            professor.is_active = True
            professor.save()
            grupo, _ = Group.objects.get_or_create(name='Professores')
            professor.groups.add(grupo)
            messages.success(
                request,
                f'Professor {professor.get_full_name()} criado com sucesso!'
            )
            return redirect('usuarios:lista_professores')
    else:
        form = CriarProfessorForm(admin_mode=is_admin)
    return render(
        request,
        'usuarios/professor_form.html',
        {'form': form, 'titulo': 'Novo Professor'},
    )


@login_required
@responsavel_campus_required
def editar_professor(request, uuid):
    is_admin = request.user.is_administrador()
    if is_admin:
        professor = get_object_or_404(
            Usuario, uuid=uuid, groups__name='Professores'
        )
    else:
        professor = get_object_or_404(
            Usuario, uuid=uuid, groups__name='Professores',
            campus=request.user.campus
        )
    if request.method == 'POST':
        form = CriarProfessorForm(
            request.POST, instance=professor, admin_mode=is_admin
        )
        if form.is_valid():
            saved = form.save(commit=False)
            if is_admin:
                saved.campus = form.cleaned_data['campus']
            saved.save()
            messages.success(request, 'Professor atualizado com sucesso!')
            return redirect('usuarios:lista_professores')
    else:
        form = CriarProfessorForm(instance=professor, admin_mode=is_admin)
    return render(
        request,
        'usuarios/professor_form.html',
        {'form': form, 'titulo': 'Editar Professor', 'professor': professor},
    )


@login_required
@responsavel_campus_required
def desativar_professor(request, uuid):
    is_admin = request.user.is_administrador()
    if is_admin:
        professor = get_object_or_404(
            Usuario, uuid=uuid, groups__name='Professores'
        )
    else:
        professor = get_object_or_404(
            Usuario, uuid=uuid, groups__name='Professores',
            campus=request.user.campus
        )
    if request.method == 'POST':
        professor.is_active = not professor.is_active
        professor.save()
        status = 'ativado' if professor.is_active else 'desativado'
        messages.success(request, f'Professor {status} com sucesso!')
        return redirect('usuarios:lista_professores')
    return render(
        request,
        'usuarios/professor_desativar.html',
        {'professor': professor},
    )
