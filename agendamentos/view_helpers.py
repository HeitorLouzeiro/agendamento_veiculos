"""
View helpers para relatórios de agendamentos.

Este módulo contém funções auxiliares para preparar dados de relatórios,
separando lógica de apresentação das views principais.
"""

import calendar

from django.db import models
from django.db.models import Count, Sum
from django.utils import timezone

from common.constants import NOMES_MESES
from cursos.models import Curso
from usuarios.models import Usuario
from veiculos.models import Veiculo

from .services import RelatorioService


def preparar_dados_relatorio_geral(agendamentos, ano, mes, filtros):
    """
    Prepara dados para o relatório geral.

    Args:
        agendamentos: QuerySet de agendamentos
        ano: Ano do relatório
        mes: Mês do relatório
        filtros: Dict com filtros aplicados

    Returns:
        dict: Dados preparados para o template
    """
    # Estatísticas por status
    stats_status = RelatorioService.obter_estatisticas_status(agendamentos)

    # Estatísticas por curso
    agendamentos_aprovados = agendamentos.filter(status='aprovado')
    cursos_km = RelatorioService.obter_estatisticas_cursos(
        agendamentos_aprovados
    )

    # Professores com estatísticas
    professores_stats = RelatorioService.obter_estatisticas_professores(
        agendamentos
    )

    # Veículos com estatísticas
    veiculos_stats = Veiculo.objects.filter(
        agendamentos__in=agendamentos
    ).annotate(
        total_agendamentos=models.Count('agendamentos'),
        total_km=Sum(
            'agendamentos__trajetos__quilometragem',
            filter=models.Q(agendamentos__status='aprovado')
        )
    ).order_by('-total_agendamentos')

    # Total de KM
    total_km = sum(dados['km_total'] for dados in cursos_km.values())

    return {
        'stats_status': stats_status,
        'cursos_km': cursos_km,
        'professores_stats': professores_stats,
        'veiculos_stats': veiculos_stats,
        'total_km': total_km,
        'ano_atual': ano,
        'mes_atual': mes,
        'nome_mes': NOMES_MESES[mes],
        **filtros
    }


def preparar_dados_relatorio_curso(curso, ano):
    """
    Prepara dados para o relatório por curso.

    Args:
        curso: Objeto Curso
        ano: Ano do relatório

    Returns:
        dict: Dados preparados para o template
    """
    from .models import Agendamento

    dados_mensais = []
    total_km_ano = 0

    for mes_num in range(1, 13):
        agendamentos_mes = Agendamento.objects.filter(
            curso=curso,
            status='aprovado',
            data_inicio__year=ano,
            data_inicio__month=mes_num
        )

        km_mes = sum(a.get_total_km() for a in agendamentos_mes)
        total_agendamentos_mes = agendamentos_mes.count()

        percentual_limite = 0
        if curso.limite_km_mensal > 0:
            percentual_limite = (
                km_mes / curso.limite_km_mensal
            ) * 100

        dados_mensais.append({
            'mes_numero': mes_num,
            'mes_nome': NOMES_MESES[mes_num],
            'km_utilizados': km_mes,
            'agendamentos': total_agendamentos_mes,
            'percentual_limite': percentual_limite,
            'km_disponiveis': curso.limite_km_mensal - km_mes
        })

        total_km_ano += km_mes

    # Agendamentos do ano
    agendamentos_ano = Agendamento.objects.filter(
        curso=curso,
        data_inicio__year=ano
    ).select_related('professor', 'veiculo').order_by('-data_inicio')

    # Estatísticas do ano
    limite_anual = curso.limite_km_mensal * 12
    percentual_uso_anual = 0
    if limite_anual > 0:
        percentual_uso_anual = (total_km_ano / limite_anual) * 100

    stats_ano = {
        'total_km': total_km_ano,
        'limite_anual': limite_anual,
        'percentual_uso_anual': percentual_uso_anual,
        'total_agendamentos': agendamentos_ano.count(),
        'agendamentos_aprovados': agendamentos_ano.filter(
            status='aprovado'
        ).count(),
        'agendamentos_pendentes': agendamentos_ano.filter(
            status='pendente'
        ).count(),
        'agendamentos_reprovados': agendamentos_ano.filter(
            status='reprovado'
        ).count(),
    }

    return {
        'curso': curso,
        'ano': ano,
        'dados_mensais': dados_mensais,
        'agendamentos_ano': agendamentos_ano,
        'stats_ano': stats_ano,
    }


def preparar_dados_relatorio_professor(professor, agendamentos):
    """
    Prepara dados para o relatório por professor.

    Args:
        professor: Objeto Usuario (professor)
        agendamentos: QuerySet de agendamentos do professor

    Returns:
        dict: Dados preparados para o template
    """
    total_agendamentos = agendamentos.count()
    total_km = sum(a.get_total_km() for a in agendamentos)

    estatisticas = {
        'total_agendamentos': total_agendamentos,
        'pendentes': agendamentos.filter(status='pendente').count(),
        'aprovados': agendamentos.filter(status='aprovado').count(),
        'reprovados': agendamentos.filter(status='reprovado').count(),
        'total_km': total_km,
        'agendamentos_por_curso': agendamentos.values(
            'curso__nome'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5],
        'veiculos_utilizados': agendamentos.values(
            'veiculo__marca',
            'veiculo__modelo',
            'veiculo__placa'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5],
    }

    return {
        'professor': professor,
        'estatisticas': estatisticas,
        'agendamentos': agendamentos,
    }


def preparar_dados_exportacao_geral(agendamentos, ano, mes, filtros):
    """
    Prepara dados para exportação de relatório geral.

    Args:
        agendamentos: QuerySet de agendamentos
        ano: Ano do relatório
        mes: Mês do relatório
        filtros: Dict com filtros aplicados

    Returns:
        dict: Dados preparados para exportação
    """
    # Estatísticas de cursos
    agendamentos_aprovados = agendamentos.filter(status='aprovado')
    cursos_km = RelatorioService.obter_estatisticas_cursos(
        agendamentos_aprovados
    )

    # Professores com estatísticas
    professores_stats = RelatorioService.obter_estatisticas_professores(
        agendamentos
    )

    # Cursos com KM (para PDF)
    cursos_km_list = Curso.objects.filter(
        agendamentos__in=agendamentos_aprovados
    ).annotate(
        total_km=Sum('agendamentos__trajetos__quilometragem')
    ).order_by('-total_km')

    # Veículos com estatísticas
    veiculos_stats = Veiculo.objects.filter(
        agendamentos__in=agendamentos
    ).annotate(
        total_agendamentos=models.Count('agendamentos'),
        total_km=Sum(
            'agendamentos__trajetos__quilometragem',
            filter=models.Q(agendamentos__status='aprovado')
        )
    ).order_by('-total_agendamentos')

    # Professores com KM (para PDF)
    professores_km = Usuario.objects.filter(
        tipo_usuario='professor',
        agendamentos__in=agendamentos_aprovados
    ).annotate(
        total_km=Sum('agendamentos__trajetos__quilometragem'),
        total_agendamentos=models.Count(
            'agendamentos',
            filter=models.Q(agendamentos__status='aprovado')
        )
    ).order_by('-total_km')

    curso_nome = 'Todos os Cursos'
    if filtros.get('curso_id'):
        try:
            curso = Curso.objects.get(id=filtros['curso_id'])
            curso_nome = curso.nome
        except Curso.DoesNotExist:
            pass

    return {
        'agendamentos': agendamentos,
        'ano': ano,
        'mes': mes,
        'cursos_km': cursos_km,
        'professores_stats': professores_stats,
        'cursos_km_list': cursos_km_list,
        'veiculos_stats': veiculos_stats,
        'professores_km': professores_km,
        'curso_nome': curso_nome,
        'status': filtros.get('status'),
    }


def obter_opcoes_filtros():
    """
    Retorna opções disponíveis para filtros de relatórios.

    Returns:
        dict: Dicionário com opções de filtros
    """
    from common.constants import MESES_DO_ANO

    from .models import Agendamento

    hoje = timezone.now()

    return {
        'anos_disponiveis': list(range(2023, hoje.year + 2)),
        'meses_disponiveis': MESES_DO_ANO,
        'cursos_disponiveis': Curso.objects.filter(ativo=True),
        'status_choices': Agendamento.STATUS_CHOICES,
    }
