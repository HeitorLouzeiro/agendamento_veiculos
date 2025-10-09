"""
Views para geração de relatórios de agendamentos.

Este módulo contém views para visualização de relatórios gerais,
por curso e por professor.
"""

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from common.constants import (AGENDAMENTOS_RELATORIO_POR_PAGINA,
                              PROFESSORES_POR_PAGINA, VEICULOS_POR_PAGINA)
from common.decorators import is_administrador
from common.pagination import PaginationHelper
from cursos.models import Curso

from ..models import Agendamento
from ..services import RelatorioService
from ..view_helpers import (obter_opcoes_filtros,
                            preparar_dados_relatorio_curso,
                            preparar_dados_relatorio_geral,
                            preparar_dados_relatorio_professor)


@login_required
@user_passes_test(is_administrador)
def relatorio_geral(request):
    """Relatório geral do sistema de agendamentos."""
    # Obter parâmetros
    hoje = timezone.now()
    ano = int(request.GET.get('ano', hoje.year))
    mes = int(request.GET.get('mes', hoje.month))

    # Buscar agendamentos base
    agendamentos = Agendamento.objects.filter(
        data_inicio__year=ano,
        data_inicio__month=mes
    ).select_related('curso', 'professor', 'veiculo')

    # Aplicar filtros usando service
    filtros = {
        'curso_id': request.GET.get('curso'),
        'status': request.GET.get('status'),
    }
    agendamentos = RelatorioService.aplicar_filtros(agendamentos, filtros)

    # Preparar dados usando view_helper
    dados = preparar_dados_relatorio_geral(agendamentos, ano, mes, filtros)

    # Paginação dos agendamentos principais
    agendamentos_ordenados = agendamentos.order_by('-criado_em')
    pagination = PaginationHelper(
        agendamentos_ordenados,
        AGENDAMENTOS_RELATORIO_POR_PAGINA
    )
    agendamentos_paginados = pagination.get_page(request.GET.get('page'))

    # Paginação de veículos
    veiculos_pagination = PaginationHelper(
        dados['veiculos_stats'],
        VEICULOS_POR_PAGINA
    )
    veiculos_paginados = veiculos_pagination.get_page(
        request.GET.get('page_veiculos')
    )

    # Paginação de professores
    professores_pagination = PaginationHelper(
        dados['professores_stats'],
        PROFESSORES_POR_PAGINA
    )
    professores_paginados = professores_pagination.get_page(
        request.GET.get('page_professores')
    )

    # Obter opções para filtros
    opcoes_filtros = obter_opcoes_filtros()

    # Montar context
    context = {
        'stats_status': dados['stats_status'],
        'cursos_km': dados['cursos_km'],
        'total_km': dados['total_km'],
        'veiculos_stats': veiculos_paginados,
        'professores_stats': professores_paginados,
        'agendamentos': agendamentos_paginados,
        'total_agendamentos_periodo': agendamentos_ordenados.count(),
        'ano_atual': ano,
        'mes_atual': mes,
        'nome_mes': dados['nome_mes'],
        'curso_atual': filtros['curso_id'],
        'status_atual': filtros['status'],
        'anos_disponiveis': opcoes_filtros['anos_disponiveis'],
        'meses_disponiveis': opcoes_filtros['meses_disponiveis'],
        'cursos_disponiveis': opcoes_filtros['cursos_disponiveis'],
        'status_choices': Agendamento.STATUS_CHOICES,
    }

    return render(request, 'agendamentos/relatorio_geral.html', context)


@login_required
@user_passes_test(is_administrador)
def relatorio_por_curso(request):
    """Relatório detalhado por curso."""
    # Obter parâmetros
    curso_id = request.GET.get('curso')
    hoje = timezone.now()
    ano = int(request.GET.get('ano', hoje.year))

    # Se não especificar curso, pegar o primeiro ativo
    if not curso_id:
        primeiro_curso = Curso.objects.filter(ativo=True).first()
        if primeiro_curso:
            curso_id = primeiro_curso.id

    curso = get_object_or_404(Curso, id=curso_id)

    # Preparar dados usando view_helper
    dados = preparar_dados_relatorio_curso(curso, ano)

    # Aplicar paginação aos agendamentos do ano
    agendamentos_ordenados = dados['agendamentos_ano'].order_by('-data_inicio')
    pagination = PaginationHelper(
        agendamentos_ordenados,
        AGENDAMENTOS_RELATORIO_POR_PAGINA
    )
    agendamentos_paginados = pagination.get_page(request.GET.get('page'))

    # Obter opções para filtros
    opcoes_filtros = obter_opcoes_filtros()

    context = {
        'curso': curso,
        'ano': ano,
        'dados_mensais': dados['dados_mensais'],
        'agendamentos_ano': agendamentos_paginados,
        'total_agendamentos_ano': agendamentos_ordenados.count(),
        'stats_ano': dados['stats_ano'],
        'cursos_disponiveis': opcoes_filtros['cursos_disponiveis'],
        'anos_disponiveis': opcoes_filtros['anos_disponiveis'],
    }

    return render(request, 'agendamentos/relatorio_por_curso.html', context)


@login_required
@user_passes_test(is_administrador)
def relatorio_por_professor(request):
    """Gera relatório detalhado por professor específico."""
    from usuarios.models import Usuario

    # Obter lista de professores
    professores = Usuario.objects.filter(
        tipo_usuario='professor'
    ).order_by('first_name', 'last_name')

    # Obter filtros
    professor_id = request.GET.get('professor')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    status = request.GET.get('status', '')

    # Professor selecionado
    professor_selecionado = None
    agendamentos = Agendamento.objects.none()
    dados = {}

    if professor_id:
        try:
            professor_selecionado = Usuario.objects.get(
                id=professor_id,
                tipo_usuario='professor'
            )

            # Filtrar agendamentos
            agendamentos = Agendamento.objects.filter(
                professor=professor_selecionado
            )

            if data_inicio:
                agendamentos = agendamentos.filter(
                    data_inicio__gte=data_inicio
                )
            if data_fim:
                agendamentos = agendamentos.filter(data_fim__lte=data_fim)
            if status:
                agendamentos = agendamentos.filter(status=status)

            agendamentos = agendamentos.order_by('-criado_em')

            # Preparar dados usando view_helper
            dados = preparar_dados_relatorio_professor(
                professor_selecionado,
                agendamentos
            )

        except Usuario.DoesNotExist:
            professor_selecionado = None

    # Paginação com helper
    pagination = PaginationHelper(
        agendamentos,
        AGENDAMENTOS_RELATORIO_POR_PAGINA
    )
    agendamentos_paginados = pagination.get_page(request.GET.get('page'))

    context = {
        'professores': professores,
        'professor_selecionado': professor_selecionado,
        'agendamentos': agendamentos_paginados,
        'estatisticas': dados.get('estatisticas', {}),
        'professor_filter': professor_id,
        'data_inicio_filter': data_inicio,
        'data_fim_filter': data_fim,
        'status_filter': status,
        'status_choices': Agendamento.STATUS_CHOICES,
    }

    return render(
        request,
        'agendamentos/relatorio_por_professor.html',
        context
    )
