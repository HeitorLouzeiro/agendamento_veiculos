"""
Views CRUD para gerenciamento de agendamentos.

Este módulo contém views para operações básicas de Create, Read, Update e
Delete de agendamentos.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from common.constants import AGENDAMENTOS_POR_PAGINA
from common.pagination import PaginationHelper
from cursos.models import Curso

from ..forms import AgendamentoForm, TrajetoFormSet, TrajetoFormSetEdit
from ..models import Agendamento, Trajeto
from ..services import AgendamentoService, RelatorioService


@login_required
def lista_agendamentos(request):
    """Lista agendamentos que o próprio usuário criou."""
    # Todos os usuários (professores e administradores) veem apenas
    # os agendamentos que eles mesmos criaram
    agendamentos = Agendamento.objects.filter(
        professor=request.user
    )

    agendamentos = agendamentos.select_related(
        'curso', 'professor', 'veiculo'
    )

    # Aplicar filtros usando service
    filtros = {
        'status': request.GET.get('status'),
        'curso_id': request.GET.get('curso'),
        'professor_search': request.GET.get('professor'),
    }
    agendamentos = RelatorioService.aplicar_filtros(agendamentos, filtros)

    # Ordenação
    agendamentos = agendamentos.order_by('-criado_em')

    # Paginação com helper
    pagination = PaginationHelper(agendamentos, AGENDAMENTOS_POR_PAGINA)
    agendamentos_paginados = pagination.get_page(request.GET.get('page'))

    context = {
        'agendamentos': agendamentos_paginados,
        'status_filter': filtros['status'],
        'curso_filter': filtros['curso_id'],
        'professor_filter': filtros['professor_search'],
        'cursos_disponiveis': Curso.objects.filter(ativo=True),
    }

    return render(request, 'agendamentos/lista.html', context)


@login_required
def criar_agendamento(request):
    """Cria um novo agendamento."""
    if request.method == 'POST':
        form = AgendamentoForm(request.POST, user=request.user)
        formset = TrajetoFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            try:
                agendamento = AgendamentoService.criar_agendamento(
                    form=form,
                    formset=formset,
                    usuario=request.user
                )
                messages.success(
                    request,
                    'Agendamento criado com sucesso! '
                    'Aguarde a aprovação do administrador.'
                )
                return redirect('agendamentos:detalhe', pk=agendamento.pk)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = AgendamentoForm(user=request.user)
        formset = TrajetoFormSet()

    context = {
        'form': form,
        'formset': formset,
        'titulo': 'Novo Agendamento'
    }
    return render(request, 'agendamentos/form.html', context)


@login_required
def editar_agendamento(request, pk):
    """Edita um agendamento existente."""
    agendamento = get_object_or_404(Agendamento, pk=pk)

    # Verificar permissões usando service
    pode_editar, mensagem_erro = AgendamentoService.pode_editar(
        agendamento,
        request.user
    )

    if not pode_editar:
        messages.error(request, mensagem_erro)
        return redirect('agendamentos:lista')

    if request.method == 'POST':
        form = AgendamentoForm(
            request.POST,
            instance=agendamento,
            user=request.user
        )
        formset = TrajetoFormSetEdit(request.POST, instance=agendamento)

        if form.is_valid() and formset.is_valid():
            try:
                agendamento = AgendamentoService.editar_agendamento(
                    form=form,
                    formset=formset,
                    agendamento=agendamento
                )
                messages.success(
                    request,
                    'Agendamento atualizado com sucesso!'
                )
                return redirect('agendamentos:detalhe', pk=agendamento.pk)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = AgendamentoForm(instance=agendamento, user=request.user)
        formset = TrajetoFormSetEdit(instance=agendamento)

    context = {
        'form': form,
        'formset': formset,
        'titulo': 'Editar Agendamento',
        'agendamento': agendamento,
        'is_edit': True
    }
    return render(request, 'agendamentos/form.html', context)


@login_required
def detalhe_agendamento(request, pk):
    """Exibe detalhes de um agendamento."""
    agendamento = get_object_or_404(Agendamento, pk=pk)

    # Verificar permissões de visualização:
    # - Administradores podem ver tudo
    # - Donos podem ver seus próprios agendamentos
    # - Outros professores não podem ver detalhes
    is_owner = agendamento.professor == request.user
    is_admin = request.user.is_administrador()
    is_responsavel = request.user.is_responsavel_campus()

    if not is_admin and not is_responsavel and not is_owner:
        messages.error(
            request,
            'Você não tem permissão para visualizar este agendamento.'
        )
        return redirect('agendamentos:lista')

    # Verificar se pode editar
    can_edit = (
        request.user.is_administrador() or
        agendamento.professor == request.user
    )

    trajetos = agendamento.trajetos.select_related('motorista').all()
    total_km = agendamento.get_total_km()

    # Lista de motoristas disponíveis para atribuição (admin/responsável)
    motoristas = []
    if is_admin or is_responsavel:
        from usuarios.models import Usuario
        motoristas = (
            Usuario.objects
            .filter(groups__name='Motoristas', is_active=True)
            .order_by('first_name', 'last_name')
        )

    context = {
        'agendamento': agendamento,
        'trajetos': trajetos,
        'total_km': total_km,
        'can_edit': can_edit,
        'motoristas': motoristas,
        'can_atribuir': is_admin or is_responsavel,
    }

    return render(request, 'agendamentos/detalhe.html', context)


@login_required
def deletar_agendamento(request, pk):
    """Deleta um agendamento."""
    agendamento = get_object_or_404(Agendamento, pk=pk)

    # Verificar permissões usando service
    pode_deletar, mensagem_erro = AgendamentoService.pode_deletar(
        agendamento,
        request.user
    )

    if not pode_deletar:
        messages.error(request, mensagem_erro)
        return redirect('agendamentos:lista')

    if request.method == 'POST':
        agendamento.delete()
        messages.success(request, 'Agendamento deletado com sucesso!')
        return redirect('agendamentos:lista')

    context = {'agendamento': agendamento}
    return render(request, 'agendamentos/deletar.html', context)


@login_required
def atribuir_motorista_trajeto(request, pk):
    """Atribui ou remove motorista de um trajeto (admin/responsável)."""
    if not (request.user.is_administrador() or request.user.is_responsavel_campus()):
        messages.error(request, 'Acesso não autorizado.')
        return redirect('agendamentos:lista')

    trajeto = get_object_or_404(Trajeto, pk=pk)

    if request.method == 'POST':
        motorista_id = request.POST.get('motorista_id') or None
        if motorista_id:
            from usuarios.models import Usuario
            motorista = get_object_or_404(
                Usuario, pk=motorista_id, groups__name='Motoristas'
            )
            trajeto.motorista = motorista
            nome = motorista.get_full_name() or motorista.username
            messages.success(
                request,
                f'Motorista "{nome}" atribuído ao trajeto com sucesso.',
            )
        else:
            trajeto.motorista = None
            messages.success(request, 'Motorista removido do trajeto.')
        trajeto.save(update_fields=['motorista'])

    return redirect('agendamentos:detalhe', pk=trajeto.agendamento_id)
