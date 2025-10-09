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
from ..models import Agendamento
from ..services import AgendamentoService, RelatorioService


@login_required
def lista_agendamentos(request):
    """Lista agendamentos do usuário (ou todos se admin)."""
    # Obter agendamentos base
    if request.user.is_administrador():
        agendamentos = Agendamento.objects.all()
    else:
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

    # Verificar se pode editar
    can_edit = (
        request.user.is_administrador() or
        agendamento.professor == request.user
    )

    trajetos = agendamento.trajetos.all()
    total_km = agendamento.get_total_km()

    context = {
        'agendamento': agendamento,
        'trajetos': trajetos,
        'total_km': total_km,
        'can_edit': can_edit
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
