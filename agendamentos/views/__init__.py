"""
Package de views do aplicativo agendamentos.

Este módulo organiza as views em arquivos separados por funcionalidade,
facilitando a manutenção e seguindo o princípio da Responsabilidade Única.

Estrutura:
- crud_views.py: Operações CRUD (Create, Read, Update, Delete)
- aprovacao_views.py: Aprovação e reprovação de agendamentos
- calendario_views.py: Dados para visualização em calendário
- relatorio_views.py: Relatórios gerais, por curso e por professor
- export_views.py: Exportação de relatórios (Excel e PDF)
"""

# Importar views de aprovação
from .aprovacao_views import (aprovacao_agendamentos, aprovar_agendamento,
                              reprovar_agendamento)
# Importar views de calendário
from .calendario_views import agendamentos_json
# Importar views CRUD
from .crud_views import (criar_agendamento, deletar_agendamento,
                         detalhe_agendamento, editar_agendamento,
                         lista_agendamentos)
# Importar views de exportação
from .export_views import (exportar_curso_excel, exportar_professor_excel,
                           exportar_professor_pdf, exportar_relatorio_excel,
                           exportar_relatorio_pdf)
# Importar views de relatórios
from .relatorio_views import (relatorio_geral, relatorio_por_curso,
                              relatorio_por_professor)

# Definir exportações públicas
__all__ = [
    # CRUD
    'lista_agendamentos',
    'criar_agendamento',
    'editar_agendamento',
    'detalhe_agendamento',
    'deletar_agendamento',
    # Aprovação
    'aprovacao_agendamentos',
    'aprovar_agendamento',
    'reprovar_agendamento',
    # Calendário
    'agendamentos_json',
    # Relatórios
    'relatorio_geral',
    'relatorio_por_curso',
    'relatorio_por_professor',
    # Exportação
    'exportar_relatorio_excel',
    'exportar_relatorio_pdf',
    'exportar_curso_excel',
    'exportar_professor_excel',
    'exportar_professor_pdf',
]
