"""
Exportador de relatórios em formato Excel.

Este módulo contém classes especializadas para exportar relatórios
de agendamentos em formato Excel (.xlsx).
"""

import io

import xlsxwriter
from django.http import HttpResponse

from common.constants import NOMES_MESES

from .base import BaseExporter


class ExcelExporter(BaseExporter):
    """
    Exportador base para relatórios em Excel.
    """

    def __init__(self, dados, titulo, filename):
        """
        Inicializa o exportador Excel.

        Args:
            dados: Dados a serem exportados
            titulo: Título do relatório
            filename: Nome do arquivo
        """
        super().__init__(dados)
        self.titulo = titulo
        self.filename = filename
        self.output = io.BytesIO()
        self.workbook = None
        self.formats = {}

    def criar_formatos(self):
        """Cria os formatos de células usados no Excel."""
        self.formats['title'] = self.workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter'
        })

        self.formats['header'] = self.workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'align': 'center',
            'border': 1
        })

        self.formats['cell'] = self.workbook.add_format({
            'border': 1,
            'align': 'left'
        })

        self.formats['number'] = self.workbook.add_format({
            'border': 1,
            'align': 'right',
            'num_format': '#,##0'
        })

    def get_content_type(self):
        """Retorna o content-type para Excel."""
        return (
            'application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.sheet'
        )

    def get_filename(self):
        """Retorna o nome do arquivo."""
        return self.filename


class AgendamentosExcelExporter(ExcelExporter):
    """
    Exportador específico para relatórios gerais de agendamentos.
    """

    def exportar(self):
        """
        Exporta relatório geral de agendamentos em Excel.

        Returns:
            HttpResponse: Resposta HTTP com o arquivo Excel
        """
        self.workbook = xlsxwriter.Workbook(self.output)
        self.criar_formatos()

        # Criar abas
        self._criar_aba_agendamentos()
        self._criar_aba_estatisticas_curso()
        self._criar_aba_estatisticas_professor()

        self.workbook.close()
        self.output.seek(0)

        response = HttpResponse(
            self.output.read(),
            content_type=self.get_content_type()
        )
        response['Content-Disposition'] = (
            f'attachment; filename="{self.get_filename()}"'
        )

        return response

    def _criar_aba_agendamentos(self):
        """Cria a aba principal com lista de agendamentos."""
        worksheet = self.workbook.add_worksheet('Agendamentos')

        # Título
        worksheet.merge_range('A1:H1', self.titulo, self.formats['title'])

        # Cabeçalhos
        headers = [
            'Data Início',
            'Data Fim',
            'Curso',
            'Professor',
            'Veículo',
            'Status',
            'KM Total',
            'Observações'
        ]

        for col, header in enumerate(headers):
            worksheet.write(2, col, header, self.formats['header'])

        # Dados
        agendamentos = self.dados['agendamentos']
        row = 3
        for agendamento in agendamentos.order_by('-data_inicio'):
            worksheet.write(
                row, 0,
                agendamento.data_inicio.strftime('%d/%m/%Y %H:%M'),
                self.formats['cell']
            )
            worksheet.write(
                row, 1,
                agendamento.data_fim.strftime('%d/%m/%Y %H:%M'),
                self.formats['cell']
            )
            worksheet.write(
                row, 2,
                agendamento.curso.nome,
                self.formats['cell']
            )
            worksheet.write(
                row, 3,
                agendamento.professor.get_full_name(),
                self.formats['cell']
            )
            veiculo_info = (
                f"{agendamento.veiculo.placa} - "
                f"{agendamento.veiculo.marca} "
                f"{agendamento.veiculo.modelo}"
            )
            worksheet.write(row, 4, veiculo_info, self.formats['cell'])
            worksheet.write(
                row, 5,
                agendamento.get_status_display(),
                self.formats['cell']
            )
            worksheet.write(
                row, 6,
                agendamento.get_total_km(),
                self.formats['number']
            )
            worksheet.write(
                row, 7,
                agendamento.observacoes or '',
                self.formats['cell']
            )
            row += 1

        # Ajustar largura das colunas
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 25)
        worksheet.set_column('E:E', 25)
        worksheet.set_column('F:F', 12)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 30)

    def _criar_aba_estatisticas_curso(self):
        """Cria aba com estatísticas por curso."""
        worksheet = self.workbook.add_worksheet('Estatísticas por Curso')
        mes = self.dados.get('mes', 1)
        ano = self.dados.get('ano', 2024)

        titulo = (
            f'Estatísticas por Curso - {NOMES_MESES[mes]} {ano}'
        )
        worksheet.merge_range('A1:F1', titulo, self.formats['title'])

        # Cabeçalhos
        headers = [
            'Curso',
            'KM Utilizados',
            'Limite Mensal',
            'KM Disponíveis',
            '% Uso',
            'Agendamentos'
        ]
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, self.formats['header'])

        # Dados
        cursos_km = self.dados.get('cursos_km', {})
        row = 3
        for curso_nome, dados in cursos_km.items():
            percentual = (
                dados['km_total'] / dados['limite_mensal'] * 100
                if dados['limite_mensal'] > 0 else 0
            )
            km_disponiveis = dados['limite_mensal'] - dados['km_total']

            worksheet.write(row, 0, curso_nome, self.formats['cell'])
            worksheet.write(
                row, 1,
                dados['km_total'],
                self.formats['number']
            )
            worksheet.write(
                row, 2,
                dados['limite_mensal'],
                self.formats['number']
            )
            worksheet.write(
                row, 3,
                km_disponiveis,
                self.formats['number']
            )
            worksheet.write(
                row, 4,
                f"{percentual:.1f}%",
                self.formats['cell']
            )
            worksheet.write(
                row, 5,
                dados['agendamentos'],
                self.formats['number']
            )
            row += 1

        # Ajustar colunas
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:E', 15)
        worksheet.set_column('F:F', 15)

    def _criar_aba_estatisticas_professor(self):
        """Cria aba com estatísticas por professor."""
        worksheet = self.workbook.add_worksheet(
            'Estatísticas por Professor'
        )
        mes = self.dados.get('mes', 1)
        ano = self.dados.get('ano', 2024)

        titulo = (
            f'Estatísticas por Professor - {NOMES_MESES[mes]} {ano}'
        )
        worksheet.merge_range('A1:H1', titulo, self.formats['title'])

        # Cabeçalhos
        headers = [
            'Professor',
            'Email',
            'Total KM',
            'Agendamentos',
            'Aprovados',
            'Pendentes',
            'Reprovados',
            'KM Médio/Agend.'
        ]
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, self.formats['header'])

        # Dados
        professores_stats = self.dados.get('professores_stats', [])
        row = 3
        for stats in professores_stats:
            total_agendamentos = stats['total_agendamentos']
            km_medio = (
                stats['total_km'] / total_agendamentos
                if total_agendamentos > 0 else 0
            )

            worksheet.write(
                row, 0,
                stats['professor'].get_full_name(),
                self.formats['cell']
            )
            worksheet.write(
                row, 1,
                stats['professor'].email,
                self.formats['cell']
            )
            worksheet.write(
                row, 2,
                stats['total_km'],
                self.formats['number']
            )
            worksheet.write(
                row, 3,
                total_agendamentos,
                self.formats['number']
            )
            worksheet.write(
                row, 4,
                stats['aprovados'],
                self.formats['number']
            )
            worksheet.write(
                row, 5,
                stats['pendentes'],
                self.formats['number']
            )
            worksheet.write(
                row, 6,
                stats['reprovados'],
                self.formats['number']
            )
            worksheet.write(
                row, 7,
                f"{km_medio:.2f}",
                self.formats['cell']
            )
            row += 1

        # Ajustar colunas
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 12)
        worksheet.set_column('D:G', 12)
        worksheet.set_column('H:H', 15)


class CursoExcelExporter(ExcelExporter):
    """
    Exportador para relatórios por curso.
    """

    def exportar(self):
        """
        Exporta relatório por curso em Excel.

        Returns:
            HttpResponse: Resposta HTTP com o arquivo Excel
        """
        self.workbook = xlsxwriter.Workbook(self.output)
        self.criar_formatos()

        worksheet = self.workbook.add_worksheet('Dados Mensais')
        worksheet.merge_range('A1:G1', self.titulo, self.formats['title'])

        # Cabeçalhos
        headers = [
            'Mês',
            'KM Utilizados',
            'Limite Mensal',
            'KM Disponíveis',
            '% Uso',
            'Agendamentos',
            'Status'
        ]
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, self.formats['header'])

        # Dados mensais
        curso = self.dados['curso']
        dados_mensais = self.dados['dados_mensais']
        row = 3

        for dados_mes in dados_mensais:
            percentual = dados_mes['percentual_limite']

            if percentual > 100:
                status = "Excedido"
            elif percentual > 80:
                status = "Atenção"
            else:
                status = "Normal"

            worksheet.write(
                row, 0,
                dados_mes['mes_nome'],
                self.formats['cell']
            )
            worksheet.write(
                row, 1,
                dados_mes['km_utilizados'],
                self.formats['number']
            )
            worksheet.write(
                row, 2,
                curso.limite_km_mensal,
                self.formats['number']
            )
            worksheet.write(
                row, 3,
                dados_mes['km_disponiveis'],
                self.formats['number']
            )
            worksheet.write(
                row, 4,
                f"{percentual:.1f}%",
                self.formats['cell']
            )
            worksheet.write(
                row, 5,
                dados_mes['agendamentos'],
                self.formats['number']
            )
            worksheet.write(row, 6, status, self.formats['cell'])
            row += 1

        # Ajustar larguras
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:F', 12)
        worksheet.set_column('G:G', 10)

        self.workbook.close()
        self.output.seek(0)

        response = HttpResponse(
            self.output.read(),
            content_type=self.get_content_type()
        )
        response['Content-Disposition'] = (
            f'attachment; filename="{self.get_filename()}"'
        )

        return response


class ProfessorExcelExporter(ExcelExporter):
    """
    Exportador para relatórios por professor.
    """

    def exportar(self):
        """
        Exporta relatório por professor em Excel.

        Returns:
            HttpResponse: Resposta HTTP com o arquivo Excel
        """
        self.workbook = xlsxwriter.Workbook(self.output)
        self.criar_formatos()

        # Aba de agendamentos
        self._criar_aba_agendamentos_professor()

        # Aba de estatísticas
        self._criar_aba_estatisticas()

        self.workbook.close()
        self.output.seek(0)

        response = HttpResponse(
            self.output.read(),
            content_type=self.get_content_type()
        )
        response['Content-Disposition'] = (
            f'attachment; filename="{self.get_filename()}"'
        )

        return response

    def _criar_aba_agendamentos_professor(self):
        """Cria aba com agendamentos do professor."""
        worksheet = self.workbook.add_worksheet('Agendamentos')

        # Título
        worksheet.merge_range('A1:H1', self.titulo, self.formats['title'])

        # Informações do professor
        professor = self.dados['professor']
        worksheet.write('A3', 'Email:', self.formats['header'])
        worksheet.write('B3', professor.email, self.formats['cell'])

        # Cabeçalhos
        headers = [
            'Data Início',
            'Data Fim',
            'Curso',
            'Veículo',
            'Status',
            'KM Total',
            'Destino',
            'Observações'
        ]
        for col, header in enumerate(headers):
            worksheet.write(5, col, header, self.formats['header'])

        # Dados
        agendamentos = self.dados['agendamentos']
        row = 6
        for agendamento in agendamentos:
            worksheet.write(
                row, 0,
                agendamento.data_inicio.strftime('%d/%m/%Y %H:%M'),
                self.formats['cell']
            )
            worksheet.write(
                row, 1,
                agendamento.data_fim.strftime('%d/%m/%Y %H:%M'),
                self.formats['cell']
            )
            worksheet.write(
                row, 2,
                agendamento.curso.nome,
                self.formats['cell']
            )
            veiculo_info = (
                f"{agendamento.veiculo.placa} - "
                f"{agendamento.veiculo.marca} "
                f"{agendamento.veiculo.modelo}"
            )
            worksheet.write(row, 3, veiculo_info, self.formats['cell'])
            worksheet.write(
                row, 4,
                agendamento.get_status_display(),
                self.formats['cell']
            )
            worksheet.write(
                row, 5,
                agendamento.get_total_km(),
                self.formats['number']
            )

            # Destinos
            trajetos = agendamento.trajetos.all()
            destinos = ', '.join([t.destino for t in trajetos])
            worksheet.write(row, 6, destinos, self.formats['cell'])

            worksheet.write(
                row, 7,
                agendamento.observacoes or '',
                self.formats['cell']
            )
            row += 1

        # Ajustar larguras
        worksheet.set_column('A:B', 15)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 25)
        worksheet.set_column('E:E', 12)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 30)

    def _criar_aba_estatisticas(self):
        """Cria aba com estatísticas do professor."""
        worksheet = self.workbook.add_worksheet('Estatísticas')
        professor = self.dados['professor']

        titulo = f'Estatísticas - {professor.get_full_name()}'
        worksheet.merge_range('A1:B1', titulo, self.formats['title'])

        # Dados estatísticos
        estatisticas = self.dados['estatisticas']
        stats_data = [
            ['Total de Agendamentos', estatisticas['total_agendamentos']],
            ['Total de KM', estatisticas['total_km']],
            ['Agendamentos Aprovados', estatisticas['aprovados']],
            ['Agendamentos Pendentes', estatisticas['pendentes']],
            ['Agendamentos Reprovados', estatisticas['reprovados']],
        ]

        if estatisticas['total_agendamentos'] > 0:
            km_medio = (
                estatisticas['total_km'] /
                estatisticas['total_agendamentos']
            )
            stats_data.append(
                ['KM Médio por Agendamento', f"{km_medio:.2f}"]
            )

        row = 3
        for label, value in stats_data:
            worksheet.write(row, 0, label, self.formats['header'])
            worksheet.write(row, 1, value, self.formats['cell'])
            row += 1

        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 20)
