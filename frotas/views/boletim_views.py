import io
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (HRFlowable, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

from agendamentos.models import Agendamento
from veiculos.models import Veiculo

from ..models import Abastecimento, Ocorrencia

AZUL = colors.HexColor('#0d6efd')
AZUL_CLARO = colors.HexColor('#cfe2ff')
CINZA = colors.HexColor('#f8f9fa')
VERMELHO = colors.HexColor('#dc3545')

PERIODOS = ('hoje', '7dias', '15dias', '30dias', 'personalizado')


def _resolver_periodo(request):
    """Retorna (data_inicio, data_fim, periodo) a partir dos parâmetros GET.
    """
    hoje = timezone.localdate()
    periodo = request.GET.get('periodo', 'hoje')
    if periodo not in PERIODOS:
        periodo = 'hoje'

    if periodo == '7dias':
        return hoje - timedelta(days=6), hoje, periodo
    if periodo == '15dias':
        return hoje - timedelta(days=14), hoje, periodo
    if periodo == '30dias':
        return hoje - timedelta(days=29), hoje, periodo
    if periodo == 'personalizado':
        try:
            inicio = date.fromisoformat(
                request.GET.get('data_inicio', hoje.isoformat())
            )
        except ValueError:
            inicio = hoje
        try:
            fim = date.fromisoformat(
                request.GET.get('data_fim', hoje.isoformat())
            )
        except ValueError:
            fim = hoje
        if fim < inicio:
            fim = inicio
        return inicio, fim, periodo
    # padrão: hoje
    return hoje, hoje, 'hoje'


@login_required
def boletim_diario(request):
    user = request.user
    if not user.is_administrador() and not user.is_responsavel_campus():
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, 'Acesso não autorizado.')
        return redirect('dashboard')

    data_inicio, data_fim, periodo = _resolver_periodo(request)
    veiculo_pk = request.GET.get('veiculo', '')
    multiplos_dias = data_inicio != data_fim

    veiculos_qs = Veiculo.objects.filter(ativo=True)
    if veiculo_pk:
        veiculos_qs = veiculos_qs.filter(pk=veiculo_pk)

    boletim_data = []
    for veiculo in veiculos_qs:
        agendamentos = (
            Agendamento.objects
            .filter(
                veiculo=veiculo,
                data_inicio__date__lte=data_fim,
                data_fim__date__gte=data_inicio,
                status='aprovado',
            )
            .select_related('professor', 'curso')
            .prefetch_related('trajetos', 'ocorrencias')
            .order_by('data_inicio')
        )
        abastecimentos = (
            Abastecimento.objects
            .filter(
                veiculo=veiculo,
                data_hora__date__gte=data_inicio,
                data_hora__date__lte=data_fim,
            )
            .select_related('motorista')
            .order_by('data_hora')
        )
        ocorrencias = (
            Ocorrencia.objects
            .filter(
                veiculo=veiculo,
                data_hora__date__gte=data_inicio,
                data_hora__date__lte=data_fim,
            )
            .select_related('motorista')
            .order_by('data_hora')
        )

        if not (
            agendamentos.exists()
            or abastecimentos.exists()
            or ocorrencias.exists()
        ):
            continue

        total_km = sum(a.get_total_km() for a in agendamentos)
        total_litros = sum(ab.litros_abastecidos for ab in abastecimentos)
        total_gasto = sum(ab.valor_gasto for ab in abastecimentos)
        criticas = ocorrencias.filter(gravidade='critica').count()

        boletim_data.append({
            'veiculo': veiculo,
            'agendamentos': agendamentos,
            'abastecimentos': abastecimentos,
            'ocorrencias': ocorrencias,
            'total_km': total_km,
            'total_litros': total_litros,
            'total_gasto_combustivel': total_gasto,
            'ocorrencias_criticas': criticas,
        })

    context = {
        'boletim_data': boletim_data,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'periodo': periodo,
        'multiplos_dias': multiplos_dias,
        'todos_veiculos': Veiculo.objects.filter(ativo=True),
        'veiculo_selecionado': veiculo_pk,
        'periodos': [
            ('Hoje', 'hoje'),
            ('7 dias', '7dias'),
            ('15 dias', '15dias'),
            ('30 dias', '30dias'),
            ('Personalizado', 'personalizado'),
        ],
    }
    return render(request, 'frotas/boletim/boletim_diario.html', context)


@login_required
def exportar_boletim_pdf(request):
    user = request.user
    if not user.is_administrador() and not user.is_responsavel_campus():
        from django.contrib import messages
        messages.error(request, 'Acesso não autorizado.')
        return redirect('dashboard')

    veiculo_pk = request.GET.get('veiculo', '')
    if not veiculo_pk:
        from django.contrib import messages
        messages.error(request, 'Selecione um veículo para exportar.')
        return redirect('frotas:boletim_diario')

    veiculo = get_object_or_404(Veiculo, pk=veiculo_pk)
    data_inicio, data_fim, _ = _resolver_periodo(request)

    agendamentos = (
        Agendamento.objects
        .filter(
            veiculo=veiculo,
            data_inicio__date__lte=data_fim,
            data_fim__date__gte=data_inicio,
            status='aprovado',
        )
        .select_related('professor', 'curso')
        .prefetch_related('trajetos')
        .order_by('data_inicio')
    )
    abastecimentos = (
        Abastecimento.objects
        .filter(
            veiculo=veiculo,
            data_hora__date__gte=data_inicio,
            data_hora__date__lte=data_fim,
        )
        .select_related('motorista')
        .order_by('data_hora')
    )
    ocorrencias = (
        Ocorrencia.objects
        .filter(
            veiculo=veiculo,
            data_hora__date__gte=data_inicio,
            data_hora__date__lte=data_fim,
        )
        .select_related('motorista')
        .order_by('data_hora')
    )

    total_km = sum(a.get_total_km() for a in agendamentos)
    total_litros = sum(ab.litros_abastecidos for ab in abastecimentos)
    total_gasto = sum(ab.valor_gasto for ab in abastecimentos)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=AZUL,
        spaceAfter=4,
    )
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=2,
    )
    secao_style = ParagraphStyle(
        'Secao',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=AZUL,
        spaceBefore=12,
        spaceAfter=4,
    )
    normal = styles['Normal']
    normal.fontSize = 8

    periodo_fmt = (
        f'{data_inicio:%d/%m/%Y} a {data_fim:%d/%m/%Y}'
        if data_inicio != data_fim
        else f'{data_inicio:%d/%m/%Y}'
    )

    elementos = []

    # Cabeçalho
    elementos.append(Paragraph('Boletim de Veículo', titulo_style))
    elementos.append(Paragraph(
        f'{veiculo.placa} — {veiculo.marca} {veiculo.modelo} ({veiculo.ano})',
        subtitulo_style,
    ))
    if veiculo.campus:
        elementos.append(Paragraph(
            f'Campus: {veiculo.campus.nome}', subtitulo_style
        ))
    elementos.append(Paragraph(f'Período: {periodo_fmt}', subtitulo_style))
    elementos.append(HRFlowable(width='100%', thickness=1, color=AZUL))
    elementos.append(Spacer(1, 6))

    # Resumo
    resumo_data = [
        ['Total de km', 'Total de litros', 'Gasto combustível'],
        [
            f'{total_km} km',
            f'{total_litros} L',
            f'R$ {total_gasto:.2f}',
        ],
    ]
    resumo_table = Table(resumo_data, colWidths=['33%', '33%', '34%'])
    resumo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, 1), AZUL_CLARO),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [AZUL_CLARO]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elementos.append(resumo_table)

    # Seção A: Viagens
    elementos.append(Paragraph('Viagens', secao_style))
    if agendamentos:
        viagens_data = [
            ['Professor', 'Curso', 'Início', 'Fim', 'Km', 'Trajetos'],
        ]
        for ag in agendamentos:
            trajetos = '; '.join(
                f'{t.origem}→{t.destino}' for t in ag.trajetos.all()
            ) or '—'
            viagens_data.append([
                ag.professor.get_full_name(),
                ag.curso.nome,
                ag.data_inicio.strftime('%d/%m %H:%M'),
                ag.data_fim.strftime('%d/%m %H:%M'),
                f'{ag.get_total_km()} km',
                Paragraph(trajetos, normal),
            ])
        col_w = [3.5 * cm, 3.5 * cm, 2 * cm, 2 * cm, 1.5 * cm, None]
        t = Table(viagens_data, colWidths=col_w, repeatRows=1)
        t.setStyle(_estilo_tabela())
        elementos.append(t)
    else:
        elementos.append(Paragraph('Nenhuma viagem no período.', normal))

    # Seção B: Abastecimentos
    elementos.append(Paragraph('Abastecimentos', secao_style))
    if abastecimentos:
        ab_data = [
            ['Data/Hora', 'Posto', 'Combustível', 'Litros', 'Valor (R$)',
             'Hodômetro', 'Motorista'],
        ]
        for ab in abastecimentos:
            ab_data.append([
                ab.data_hora.strftime('%d/%m %H:%M'),
                ab.local_posto,
                ab.get_tipo_combustivel_display(),
                f'{ab.litros_abastecidos} L',
                f'R$ {ab.valor_gasto:.2f}',
                f'{ab.km_atual} km',
                ab.motorista.get_full_name() if ab.motorista else '—',
            ])
        ab_data.append([
            'Total', '', '', f'{total_litros} L',
            f'R$ {total_gasto:.2f}', '', '',
        ])
        col_w = [2 * cm, 3 * cm, 2.2 * cm, 1.8 * cm,
                 2 * cm, 2 * cm, None]
        t = Table(ab_data, colWidths=col_w, repeatRows=1)
        estilo = _estilo_tabela()
        n = len(ab_data) - 1
        estilo.add('BACKGROUND', (0, n), (-1, n), AZUL_CLARO)
        estilo.add('FONTNAME', (0, n), (-1, n), 'Helvetica-Bold')
        t.setStyle(estilo)
        elementos.append(t)
    else:
        elementos.append(Paragraph('Nenhum abastecimento no período.', normal))

    # Seção C: Ocorrências
    elementos.append(Paragraph('Ocorrências', secao_style))
    if ocorrencias:
        oc_data = [
            ['Data/Hora', 'Tipo', 'Gravidade', 'Local', 'Responsável',
             'Status'],
        ]
        for oc in ocorrencias:
            oc_data.append([
                oc.data_hora.strftime('%d/%m %H:%M'),
                oc.get_tipo_display(),
                oc.get_gravidade_display(),
                oc.local,
                oc.motorista.get_full_name() if oc.motorista else '—',
                'Resolvida' if oc.resolvido else 'Pendente',
            ])
        col_w = [2 * cm, 2.5 * cm, 2 * cm, 3 * cm, None, 2 * cm]
        t = Table(oc_data, colWidths=col_w, repeatRows=1)
        estilo = _estilo_tabela()
        for i, oc in enumerate(ocorrencias, start=1):
            if oc.gravidade == 'critica':
                estilo.add('BACKGROUND', (2, i), (2, i), VERMELHO)
                estilo.add('TEXTCOLOR', (2, i), (2, i), colors.white)
        t.setStyle(estilo)
        elementos.append(t)
    else:
        elementos.append(Paragraph('Nenhuma ocorrência no período.', normal))

    # Rodapé
    elementos.append(Spacer(1, 12))
    elementos.append(HRFlowable(width='100%', thickness=0.5, color=colors.grey))
    elementos.append(Paragraph(
        f'Gerado em {timezone.localtime():%d/%m/%Y %H:%M} — '
        f'Sistema de Agendamento de Veículos UESPI',
        ParagraphStyle('Rodape', parent=normal, textColor=colors.grey,
                       fontSize=7, alignment=1),
    ))

    doc.build(elementos)
    buffer.seek(0)

    nome_arquivo = (
        f'boletim_{veiculo.placa}_{data_inicio:%Y%m%d}'
        f'{"_" + data_fim.strftime("%Y%m%d") if data_inicio != data_fim else ""}'
        '.pdf'
    )
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{nome_arquivo}"'
    )
    return response


def _estilo_tabela():
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, CINZA]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ])


@login_required
def dashboard_motorista(request):
    user = request.user
    if not user.is_motorista():
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, 'Área exclusiva para motoristas.')
        return redirect('dashboard')

    from django.db.models import Prefetch
    from agendamentos.models import Agendamento, Trajeto
    from ..models import Deslocamento

    abastecimentos = (
        Abastecimento.objects
        .filter(motorista=user)
        .select_related('veiculo')[:5]
    )
    ocorrencias = (
        Ocorrencia.objects
        .filter(motorista=user)
        .select_related('veiculo')[:5]
    )
    deslocamentos = (
        Deslocamento.objects
        .filter(motorista=user)
        .select_related('veiculo')[:5]
    )
    agendamentos_atribuidos = (
        Agendamento.objects
        .filter(trajetos__motorista=user)
        .distinct()
        .select_related('veiculo', 'curso')
        .prefetch_related(
            Prefetch(
                'trajetos',
                queryset=Trajeto.objects
                    .filter(motorista=user)
                    .order_by('data_saida'),
                to_attr='meus_trajetos',
            )
        )
        .order_by('data_inicio')
    )
    return render(request, 'frotas/dashboard_motorista.html', {
        'abastecimentos_recentes': abastecimentos,
        'ocorrencias_recentes': ocorrencias,
        'deslocamentos_recentes': deslocamentos,
        'agendamentos_atribuidos': agendamentos_atribuidos,
    })


@login_required
def dashboard_responsavel(request):
    user = request.user
    if not user.is_responsavel_campus() and not user.is_administrador():
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, 'Acesso não autorizado.')
        return redirect('dashboard')

    from usuarios.models import Usuario
    motoristas = Usuario.objects.filter(
        groups__name='Motoristas',
        campus=user.campus,
    ).order_by('first_name')

    ocorrencias_pendentes = (
        Ocorrencia.objects
        .filter(resolvido=False)
        .select_related('veiculo', 'motorista')[:10]
    )
    return render(request, 'frotas/dashboard_responsavel.html', {
        'motoristas': motoristas,
        'ocorrencias_pendentes': ocorrencias_pendentes,
    })
