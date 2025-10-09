"""
Views para aprovação e reprovação de agendamentos.

Este módulo contém views que permitem administradores aprovar ou reprovar
agendamentos pendentes.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from common.constants import AGENDAMENTOS_APROVACAO_POR_PAGINA
from common.decorators import is_administrador
from common.pagination import PaginationHelper
from cursos.models import Curso

from ..models import Agendamento
from ..services import AgendamentoService, RelatorioService


@login_required
@user_passes_test(is_administrador)
def aprovacao_agendamentos(request):
    """Lista agendamentos pendentes para aprovação."""
    # Buscar apenas agendamentos pendentes
    agendamentos = Agendamento.objects.filter(
        status='pendente'
    ).select_related('curso', 'professor', 'veiculo')

    # Aplicar filtros usando service
    filtros = {
        'curso_id': request.GET.get('curso'),
        'professor_search': request.GET.get('professor'),
    }
    agendamentos = RelatorioService.aplicar_filtros(agendamentos, filtros)

    # Ordenação
    agendamentos = agendamentos.order_by('-criado_em')

    # Paginação com helper
    pagination = PaginationHelper(
        agendamentos,
        AGENDAMENTOS_APROVACAO_POR_PAGINA
    )
    agendamentos_paginados = pagination.get_page(request.GET.get('page'))

    context = {
        'agendamentos': agendamentos_paginados,
        'curso_filter': filtros['curso_id'],
        'professor_filter': filtros['professor_search'],
        'cursos_disponiveis': Curso.objects.filter(ativo=True),
    }

    return render(request, 'agendamentos/aprovacao.html', context)


@login_required
@user_passes_test(is_administrador)
def aprovar_agendamento(request, pk):
    """Aprova um agendamento."""
    agendamento = get_object_or_404(Agendamento, pk=pk)

    if request.method == 'POST':
        try:
            AgendamentoService.aprovar_agendamento(agendamento)
            messages.success(request, 'Agendamento aprovado com sucesso!')
            return redirect('agendamentos:detalhe', pk=pk)
        except ValidationError as e:
            # Extrai a mensagem de erro corretamente
            if hasattr(e, 'message'):
                error_msg = e.message
            elif hasattr(e, 'messages') and e.messages:
                error_msg = ' '.join(e.messages)
            else:
                error_msg = str(e)
            messages.error(
                request,
                f'Erro ao aprovar agendamento: {error_msg}'
            )
            return redirect('agendamentos:detalhe', pk=pk)

    return redirect('agendamentos:detalhe', pk=pk)


@login_required
@user_passes_test(is_administrador)
def reprovar_agendamento(request, pk):
    """Reprova um agendamento."""
    agendamento = get_object_or_404(Agendamento, pk=pk)

    if request.method == 'POST':
        motivo = request.POST.get('motivo', '')
        if not motivo:
            messages.error(
                request,
                'É necessário informar o motivo da reprovação.'
            )
            return redirect('agendamentos:reprovar', pk=pk)

        AgendamentoService.reprovar_agendamento(agendamento, motivo)
        messages.success(request, 'Agendamento reprovado.')
        return redirect('agendamentos:detalhe', pk=pk)

    context = {'agendamento': agendamento}
    return render(request, 'agendamentos/reprovar.html', context)
