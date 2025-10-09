"""
Exportador de relatórios em formato PDF.

Este módulo contém classes especializadas para exportar relatórios
de agendamentos em formato PDF.
"""

import io

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

from .base import BaseExporter


class PDFExporter(BaseExporter):
    """
    Exportador base para relatórios em PDF.
    """

    def __init__(self, dados, titulo, filename):
        """
        Inicializa o exportador PDF.

        Args:
            dados: Dados a serem exportados
            titulo: Título do relatório
            filename: Nome do arquivo
        """
        super().__init__(dados)
        self.titulo = titulo
        self.filename = filename
        self.buffer = io.BytesIO()
        self.elements = []
        self.styles = getSampleStyleSheet()
        self._criar_estilos_customizados()

    def _criar_estilos_customizados(self):
        """Cria estilos personalizados para o PDF."""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=1  # Center
        )

        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12
        )

    def _criar_estilo_tabela(self):
        """Retorna o estilo padrão para tabelas."""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])

    def get_content_type(self):
        """Retorna o content-type para PDF."""
        return 'application/pdf'

    def get_filename(self):
        """Retorna o nome do arquivo."""
        return self.filename


class AgendamentosPDFExporter(PDFExporter):
    """
    Exportador específico para relatórios gerais de agendamentos.
    """

    def exportar(self):
        """
        Exporta relatório geral de agendamentos em PDF.

        Returns:
            HttpResponse: Resposta HTTP com o arquivo PDF
        """
        doc = SimpleDocTemplate(self.buffer, pagesize=A4)

        # Título
        self.elements.append(Paragraph(self.titulo, self.title_style))
        self.elements.append(Spacer(1, 12))

        # Filtros aplicados
        self._adicionar_filtros()

        # Estatísticas gerais
        self._adicionar_estatisticas_gerais()

        # Quilometragem por Curso
        self._adicionar_cursos_km()

        # Agendamentos por Veículo
        self._adicionar_veiculos_stats()

        # Quilometragem por Professor
        self._adicionar_professores_km()

        # Lista de agendamentos
        self._adicionar_lista_agendamentos()

        # Gerar PDF
        doc.build(self.elements)
        self.buffer.seek(0)

        response = HttpResponse(
            self.buffer.read(),
            content_type=self.get_content_type()
        )
        response['Content-Disposition'] = (
            f'attachment; filename="{self.get_filename()}"'
        )

        return response

    def _adicionar_filtros(self):
        """Adiciona seção de filtros aplicados."""
        curso_nome = self.dados.get('curso_nome', 'Todos os Cursos')
        filtros_text = f"<b>Filtros:</b> {curso_nome}"

        status = self.dados.get('status')
        if status:
            from agendamentos.models import Agendamento
            status_dict = dict(Agendamento.STATUS_CHOICES)
            filtros_text += f" | Status: {status_dict.get(status, status)}"

        self.elements.append(
            Paragraph(filtros_text, self.styles['Normal'])
        )
        self.elements.append(Spacer(1, 12))

    def _adicionar_estatisticas_gerais(self):
        """Adiciona estatísticas gerais ao PDF."""
        agendamentos = self.dados['agendamentos']
        total_agendamentos = agendamentos.count()
        aprovados = agendamentos.filter(status='aprovado').count()
        pendentes = agendamentos.filter(status='pendente').count()
        reprovados = agendamentos.filter(status='reprovado').count()
        total_km = sum(
            a.get_total_km()
            for a in agendamentos.filter(status='aprovado')
        )

        stats_data = [
            ['Estatísticas Gerais', '', '', ''],
            ['Total de Agendamentos', str(total_agendamentos),
             'Aprovados', str(aprovados)],
            ['Pendentes', str(pendentes), 'Reprovados', str(reprovados)],
            ['Total KM (Aprovados)', f'{total_km} km', '', '']
        ]

        stats_table = Table(
            stats_data,
            colWidths=[2*inch, 1*inch, 1.5*inch, 1*inch]
        )
        stats_table.setStyle(self._criar_estilo_tabela())
        self.elements.append(stats_table)
        self.elements.append(Spacer(1, 20))

    def _adicionar_cursos_km(self):
        """Adiciona tabela de quilometragem por curso."""
        cursos_km = self.dados.get('cursos_km_list', [])

        if cursos_km:
            self.elements.append(
                Paragraph(
                    '<b>Quilometragem por Curso (Top 10)</b>',
                    self.header_style
                )
            )
            self.elements.append(Spacer(1, 12))

            curso_data = [['Curso', 'Total KM', 'Agendamentos']]
            for curso in cursos_km[:10]:
                nome_curso = (
                    curso.nome[:30] + '...'
                    if len(curso.nome) > 30 else curso.nome
                )
                curso_data.append([
                    nome_curso,
                    f'{curso.total_km or 0} km',
                    str(self.dados['agendamentos'].filter(
                        curso=curso, status='aprovado'
                    ).count())
                ])

            curso_table = Table(
                curso_data,
                colWidths=[3*inch, 1*inch, 1*inch]
            )
            curso_table.setStyle(self._criar_estilo_tabela())
            self.elements.append(curso_table)
            self.elements.append(Spacer(1, 20))

    def _adicionar_veiculos_stats(self):
        """Adiciona estatísticas por veículo."""
        veiculos_stats = self.dados.get('veiculos_stats', [])

        if veiculos_stats:
            self.elements.append(
                Paragraph(
                    '<b>Agendamentos por Veículo (Top 10)</b>',
                    self.header_style
                )
            )
            self.elements.append(Spacer(1, 12))

            veiculo_data = [['Veículo', 'Agendamentos', 'KM Total']]
            for veiculo in veiculos_stats[:10]:
                veiculo_data.append([
                    f'{veiculo.placa} - {veiculo.marca} {veiculo.modelo}',
                    str(veiculo.total_agendamentos),
                    f'{veiculo.total_km or 0} km'
                ])

            veiculo_table = Table(
                veiculo_data,
                colWidths=[3*inch, 1*inch, 1*inch]
            )
            veiculo_table.setStyle(self._criar_estilo_tabela())
            self.elements.append(veiculo_table)
            self.elements.append(Spacer(1, 20))

    def _adicionar_professores_km(self):
        """Adiciona quilometragem por professor."""
        professores_km = self.dados.get('professores_km', [])

        if professores_km:
            self.elements.append(
                Paragraph(
                    '<b>Quilometragem por Professor (Top 10)</b>',
                    self.header_style
                )
            )
            self.elements.append(Spacer(1, 12))

            prof_data = [['Professor', 'Total KM', 'Agendamentos']]
            for professor in professores_km[:10]:
                full_name = professor.get_full_name()
                nome_prof = (
                    full_name[:25] + '...'
                    if len(full_name) > 25 else full_name
                )
                prof_data.append([
                    nome_prof,
                    f'{professor.total_km or 0} km',
                    str(professor.total_agendamentos)
                ])

            prof_table = Table(
                prof_data,
                colWidths=[3*inch, 1*inch, 1*inch]
            )
            prof_table.setStyle(self._criar_estilo_tabela())
            self.elements.append(prof_table)
            self.elements.append(Spacer(1, 20))

    def _adicionar_lista_agendamentos(self):
        """Adiciona lista de agendamentos ao PDF."""
        agendamentos = self.dados['agendamentos']

        if agendamentos.exists():
            self.elements.append(
                Paragraph(
                    '<b>Lista de Agendamentos</b>',
                    self.header_style
                )
            )
            self.elements.append(Spacer(1, 12))

            data = [[
                'Data/Hora',
                'Curso',
                'Professor',
                'Veículo',
                'Status',
                'KM'
            ]]

            # Limitar a 50 para não sobrecarregar
            for agendamento in agendamentos.order_by('-data_inicio')[:50]:
                curso_nome = agendamento.curso.nome
                if len(curso_nome) > 15:
                    curso_nome = curso_nome[:15] + '...'

                prof_nome = agendamento.professor.get_full_name()
                if len(prof_nome) > 20:
                    prof_nome = prof_nome[:20] + '...'

                data.append([
                    agendamento.data_inicio.strftime('%d/%m %H:%M'),
                    curso_nome,
                    prof_nome,
                    agendamento.veiculo.placa,
                    agendamento.get_status_display(),
                    f'{agendamento.get_total_km()} km'
                ])

            table = Table(
                data,
                colWidths=[
                    1*inch,
                    1.5*inch,
                    1.5*inch,
                    0.8*inch,
                    0.8*inch,
                    0.6*inch
                ]
            )

            style = self._criar_estilo_tabela()
            style.add('FONTSIZE', (0, 1), (-1, -1), 7)
            table.setStyle(style)
            self.elements.append(table)

            if agendamentos.count() > 50:
                self.elements.append(Spacer(1, 12))
                self.elements.append(
                    Paragraph(
                        f'<i>* Mostrando os primeiros 50 de '
                        f'{agendamentos.count()} agendamentos</i>',
                        self.styles['Normal']
                    )
                )


class ProfessorPDFExporter(PDFExporter):
    """
    Exportador para relatórios por professor.
    """

    def exportar(self):
        """
        Exporta relatório por professor em PDF.

        Returns:
            HttpResponse: Resposta HTTP com o arquivo PDF
        """
        doc = SimpleDocTemplate(self.buffer, pagesize=A4)

        # Título
        title = Paragraph(self.titulo, self.title_style)
        self.elements.append(title)
        self.elements.append(Spacer(1, 12))

        # Informações do professor
        self._adicionar_info_professor()

        # Estatísticas
        self._adicionar_estatisticas()

        # Lista de agendamentos
        self._adicionar_agendamentos()

        # Gerar PDF
        doc.build(self.elements)
        self.buffer.seek(0)

        response = HttpResponse(
            self.buffer.read(),
            content_type=self.get_content_type()
        )
        response['Content-Disposition'] = (
            f'attachment; filename="{self.get_filename()}"'
        )

        return response

    def _adicionar_info_professor(self):
        """Adiciona informações do professor."""
        professor = self.dados['professor']
        info_data = [['Email:', professor.email]]

        info_table = Table(info_data, colWidths=[100, 400])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        self.elements.append(info_table)
        self.elements.append(Spacer(1, 20))

    def _adicionar_estatisticas(self):
        """Adiciona estatísticas do professor."""
        estatisticas = self.dados['estatisticas']

        stats_title = Paragraph('<b>Estatísticas</b>', self.header_style)
        self.elements.append(stats_title)
        self.elements.append(Spacer(1, 12))

        stats_data = [
            ['Métrica', 'Valor'],
            ['Total de Agendamentos',
             str(estatisticas['total_agendamentos'])],
            ['Total de KM', f"{estatisticas['total_km']} km"],
            ['Agendamentos Aprovados', str(estatisticas['aprovados'])],
            ['Agendamentos Pendentes', str(estatisticas['pendentes'])],
            ['Agendamentos Reprovados', str(estatisticas['reprovados'])],
        ]

        stats_table = Table(stats_data, colWidths=[250, 250])
        stats_table.setStyle(self._criar_estilo_tabela())
        self.elements.append(stats_table)
        self.elements.append(Spacer(1, 20))

    def _adicionar_agendamentos(self):
        """Adiciona lista de agendamentos do professor."""
        agendamentos = self.dados['agendamentos']

        if agendamentos.exists():
            agend_title = Paragraph(
                '<b>Agendamentos</b>',
                self.header_style
            )
            self.elements.append(agend_title)
            self.elements.append(Spacer(1, 12))

            agend_data = [['Data', 'Curso', 'Veículo', 'Status', 'KM']]

            # Limitar a 20
            for agendamento in agendamentos[:20]:
                agend_data.append([
                    agendamento.data_inicio.strftime('%d/%m/%Y'),
                    agendamento.curso.nome[:15],
                    agendamento.veiculo.placa,
                    agendamento.get_status_display(),
                    str(agendamento.get_total_km())
                ])

            agend_table = Table(
                agend_data,
                colWidths=[80, 120, 80, 80, 60]
            )

            style = self._criar_estilo_tabela()
            style.add('FONTSIZE', (0, 0), (-1, -1), 8)
            agend_table.setStyle(style)
            self.elements.append(agend_table)

            if agendamentos.count() > 20:
                nota = Paragraph(
                    f'<i>Mostrando os 20 primeiros agendamentos de '
                    f'{agendamentos.count()} no total.</i>',
                    self.styles['Normal']
                )
                self.elements.append(Spacer(1, 12))
                self.elements.append(nota)
