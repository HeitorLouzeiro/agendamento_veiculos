"""
Views para visualização de agendamentos em calendário.

Este módulo fornece dados em formato JSON para integração com
bibliotecas de calendário front-end.
"""

from django.http import JsonResponse

from ..models import Agendamento


def agendamentos_json(request):
    """Retorna agendamentos em formato JSON para o calendário."""
    agendamentos = Agendamento.objects.all().select_related(
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
            # Usuário logado - informações completas
            is_owner = agendamento.professor == request.user
            is_admin = request.user.is_administrador()

            title = (
                f"{agendamento.curso.nome} - {agendamento.veiculo.placa}"
            )
            if not is_owner and not is_admin:
                prof_name = (
                    agendamento.professor.get_full_name() or
                    agendamento.professor.username
                )
                title += f" ({prof_name})"

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
