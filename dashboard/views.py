from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from agendamentos.models import Agendamento


def dashboard(request):
    """Página principal com calendário de agendamentos (público)"""
    # Obter o mês e ano do calendário (padrão: mês atual)
    try:
        mes = int(request.GET.get('mes', timezone.now().month))
        ano = int(request.GET.get('ano', timezone.now().year))
    except (ValueError, TypeError):
        mes = timezone.now().month
        ano = timezone.now().year

    # Filtrar agendamentos do mês específico
    # Administradores veem todos os agendamentos (exceto cancelados)
    # Usuários comuns veem:
    #   - Todos os agendamentos aprovados (para ver disponibilidade)
    #   - Apenas seus próprios pendentes (não mostra cancelados)
    # Usuários não autenticados veem apenas aprovados
    
    if not request.user.is_authenticated:
        # Não autenticado: apenas aprovados
        agendamentos = Agendamento.objects.filter(status='aprovado')
    elif request.user.is_administrador():
        # Admin: todos exceto cancelados
        agendamentos = Agendamento.objects.exclude(status='reprovado')
    else:
        # Usuários comuns: aprovados de todos + seus próprios pendentes
        agendamentos = Agendamento.objects.filter(
            Q(status='aprovado') |
            Q(professor=request.user, status='pendente')
        )

    agendamentos = agendamentos.select_related(
        'curso', 'professor', 'veiculo'
    ).filter(
        data_inicio__year=ano,
        data_inicio__month=mes
    ).order_by('data_inicio__day', 'data_inicio__time')

    # Paginação (6 agendamentos por página para mobile)
    paginator = Paginator(agendamentos, 6)
    page_number = request.GET.get('page')
    agendamentos_paginados = paginator.get_page(page_number)

    context = {
        'agendamentos_recentes': agendamentos_paginados,
        'mes_atual': mes,
        'ano_atual': ano,
        'nome_mes': datetime(ano, mes, 1).strftime('%B %Y').title(),
    }

    return render(request, 'dashboard/index.html', context)
