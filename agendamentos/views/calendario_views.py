"""
Views para visualização de agendamentos em calendário.

Este módulo fornece dados em formato JSON para integração com
bibliotecas de calendário front-end.
"""

from django.db.models import Q
from django.http import JsonResponse

from ..models import Agendamento


def agendamentos_json(request):
    """Retorna agendamentos em formato JSON para o calendário."""
    # Administradores veem todos os agendamentos (exceto reprovados)
    # Usuários comuns veem:
    #   - Todos os agendamentos aprovados e pendentes
    #     (para ver disponibilidade e conflitos de veículos)
    #   - Não veem detalhes de agendamentos pendentes de outros
    # Usuários não autenticados veem apenas aprovados

    if not request.user.is_authenticated:
        # Não autenticado: apenas aprovados
        agendamentos = Agendamento.objects.filter(status='aprovado')
    elif request.user.is_administrador():
        # Admin: todos exceto reprovados
        agendamentos = Agendamento.objects.exclude(status='reprovado')
    else:
        # Usuários comuns: aprovados e pendentes de todos
        agendamentos = Agendamento.objects.filter(
            Q(status='aprovado') | Q(status='pendente')
        )

    agendamentos = agendamentos.select_related(
        'professor', 'curso', 'veiculo'
    )

    # Mapa de cores por status
    cores_status = {
        'pendente': '#ffc107',   # Amarelo
        'aprovado': '#28a745',   # Verde
        'reprovado': '#dc3545',  # Vermelho
    }

    eventos = []
    for agendamento in agendamentos:
        color = cores_status.get(agendamento.status, '#6c757d')

        if request.user.is_authenticated:
            # Usuário logado
            is_owner = agendamento.professor == request.user
            is_admin = request.user.is_administrador()

            # Se não é admin e não é dono, mostra info limitada
            if not is_owner and not is_admin:
                evento = {
                    'id': agendamento.id,
                    'title': f"{agendamento.veiculo.placa} - Reservado",
                    'start': agendamento.data_inicio.isoformat(),
                    'end': agendamento.data_fim.isoformat(),
                    'color': color,
                    'extendedProps': {
                        'is_owner': False,
                        'can_edit': False,
                        'can_view': False,
                        'status': agendamento.status
                    }
                }
            else:
                # Informações completas (admin ou dono)
                title = (
                    f"{agendamento.curso.nome} - {agendamento.veiculo.placa}"
                )

                evento = {
                    'id': agendamento.id,
                    'title': title,
                    'start': agendamento.data_inicio.isoformat(),
                    'end': agendamento.data_fim.isoformat(),
                    'color': color,
                    'url': f'/agendamentos/{agendamento.id}/',
                    'extendedProps': {
                        'is_owner': is_owner,
                        'can_edit': is_admin or is_owner,
                        'can_view': True,
                        'professor_name': (
                            agendamento.professor.get_full_name() or
                            agendamento.professor.username
                        ),
                        'status': agendamento.status
                    }
                }
        else:
            # Usuário não logado - informações básicas
            evento = {
                'id': agendamento.id,
                'title': f"{agendamento.curso.nome} - Agendado",
                'start': agendamento.data_inicio.isoformat(),
                'end': agendamento.data_fim.isoformat(),
                'color': color,
                'extendedProps': {'requires_login': True}
            }

        eventos.append(evento)

    return JsonResponse(eventos, safe=False)
