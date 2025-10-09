"""
Views para exportação de relatórios em diversos formatos.

Este módulo contém views para exportar relatórios de agendamentos
em formato Excel e PDF.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from common.constants import NOMES_MESES
from common.decorators import is_administrador
from cursos.models import Curso

from ..exports.excel_exporter import (AgendamentosExcelExporter,
                                      CursoExcelExporter,
                                      ProfessorExcelExporter)
from ..exports.pdf_exporter import (AgendamentosPDFExporter,
                                    ProfessorPDFExporter)
from ..models import Agendamento
from ..services import RelatorioService
from ..view_helpers import (preparar_dados_exportacao_geral,
                            preparar_dados_relatorio_curso,
                            preparar_dados_relatorio_professor)


@login_required
@user_passes_test(is_administrador)
def exportar_relatorio_excel(request):
    """Exporta relatório geral em Excel."""
    # Obter parâmetros
    hoje = timezone.now()
    ano = int(request.GET.get('ano', hoje.year))
    mes = int(request.GET.get('mes', hoje.month))

    # Buscar agendamentos
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

    # Preparar dados para exportação
    dados = preparar_dados_exportacao_geral(
        agendamentos,
        ano,
        mes,
        filtros
    )

    # Usar exporter para criar arquivo
    titulo = f'Relatório de Agendamentos - {NOMES_MESES[mes]} {ano}'
    filename = (
        f'relatorio_agendamentos_{NOMES_MESES[mes].lower()}_{ano}.xlsx'
    )

    exporter = AgendamentosExcelExporter(dados, titulo, filename)
    return exporter.exportar()


@login_required
@user_passes_test(is_administrador)
def exportar_relatorio_pdf(request):
    """Exporta relatório geral em PDF."""
    # Obter parâmetros
    hoje = timezone.now()
    ano = int(request.GET.get('ano', hoje.year))
    mes = int(request.GET.get('mes', hoje.month))

    # Buscar agendamentos
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

    # Preparar dados para exportação
    dados = preparar_dados_exportacao_geral(
        agendamentos,
        ano,
        mes,
        filtros
    )

    # Usar exporter para criar arquivo
    titulo = f'Relatório de Agendamentos - {NOMES_MESES[mes]} {ano}'
    filename = f'relatorio_agendamentos_{NOMES_MESES[mes].lower()}_{ano}.pdf'

    exporter = AgendamentosPDFExporter(dados, titulo, filename)
    return exporter.exportar()


@login_required
@user_passes_test(is_administrador)
def exportar_curso_excel(request):
    """Exporta relatório por curso em Excel."""
    # Obter parâmetros
    curso_id = request.GET.get('curso')
    hoje = timezone.now()
    ano = int(request.GET.get('ano', hoje.year))

    # Obter curso
    if not curso_id:
        primeiro_curso = Curso.objects.filter(ativo=True).first()
        if primeiro_curso:
            curso_id = primeiro_curso.id

    curso = get_object_or_404(Curso, id=curso_id)

    # Preparar dados usando view_helper
    dados = preparar_dados_relatorio_curso(curso, ano)

    # Usar exporter para criar arquivo
    titulo = f'{curso.nome} - {ano}'
    filename = f'relatorio_{curso.nome.lower().replace(" ", "_")}_{ano}.xlsx'

    exporter = CursoExcelExporter(dados, titulo, filename)
    return exporter.exportar()


@login_required
@user_passes_test(is_administrador)
def exportar_professor_excel(request):
    """Exporta relatório por professor em Excel."""
    from usuarios.models import Usuario

    professor_id = request.GET.get('professor')

    if not professor_id:
        messages.error(request, 'Selecione um professor para exportar.')
        return redirect('agendamentos:relatorio_por_professor')

    professor = get_object_or_404(
        Usuario,
        id=professor_id,
        tipo_usuario='professor'
    )

    # Filtrar agendamentos
    agendamentos = Agendamento.objects.filter(professor=professor)

    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    status_filtro = request.GET.get('status')

    if data_inicio:
        agendamentos = agendamentos.filter(data_inicio__gte=data_inicio)
    if data_fim:
        agendamentos = agendamentos.filter(data_fim__lte=data_fim)
    if status_filtro:
        agendamentos = agendamentos.filter(status=status_filtro)

    agendamentos = agendamentos.order_by('-data_inicio')

    # Preparar dados usando view_helper
    dados = preparar_dados_relatorio_professor(professor, agendamentos)

    # Usar exporter para criar arquivo
    titulo = f'Relatório - {professor.get_full_name()}'
    nome_professor = professor.get_full_name().lower().replace(" ", "_")
    filename = f'relatorio_professor_{nome_professor}.xlsx'

    exporter = ProfessorExcelExporter(dados, titulo, filename)
    return exporter.exportar()


@login_required
@user_passes_test(is_administrador)
def exportar_professor_pdf(request):
    """Exporta relatório por professor em PDF."""
    from usuarios.models import Usuario

    professor_id = request.GET.get('professor')

    if not professor_id:
        messages.error(request, 'Selecione um professor para exportar.')
        return redirect('agendamentos:relatorio_por_professor')

    professor = get_object_or_404(
        Usuario,
        id=professor_id,
        tipo_usuario='professor'
    )

    # Filtrar agendamentos
    agendamentos = Agendamento.objects.filter(professor=professor)

    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    status_filtro = request.GET.get('status')

    if data_inicio:
        agendamentos = agendamentos.filter(data_inicio__gte=data_inicio)
    if data_fim:
        agendamentos = agendamentos.filter(data_fim__lte=data_fim)
    if status_filtro:
        agendamentos = agendamentos.filter(status=status_filtro)

    agendamentos = agendamentos.order_by('-data_inicio')

    # Preparar dados usando view_helper
    dados = preparar_dados_relatorio_professor(professor, agendamentos)

    # Usar exporter para criar arquivo
    titulo = f'Relatório - {professor.get_full_name()}'
    nome_professor = professor.get_full_name().lower().replace(" ", "_")
    filename = f'relatorio_professor_{nome_professor}.pdf'

    exporter = ProfessorPDFExporter(dados, titulo, filename)
    return exporter.exportar()
