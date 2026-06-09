import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from agendamentos.models import Trajeto
from common.pagination import PaginationHelper

from ..forms import DeslocamentoForm
from ..models import Deslocamento


@login_required
def lista_deslocamentos(request):
    user = request.user
    if user.is_administrador() or user.is_responsavel_campus():
        qs = Deslocamento.objects.select_related('veiculo', 'motorista')
    else:
        qs = Deslocamento.objects.filter(
            motorista=user
        ).select_related('veiculo')

    pagination = PaginationHelper(qs, 10)
    deslocamentos = pagination.get_page(request.GET.get('page'))
    return render(
        request,
        'frotas/deslocamentos/lista.html',
        {'deslocamentos': deslocamentos},
    )


@login_required
def criar_deslocamento(request):
    user = request.user
    is_admin = user.is_administrador() or user.is_responsavel_campus()

    if request.method == 'POST':
        form = DeslocamentoForm(request.POST, motorista=user, is_admin=is_admin)
        if form.is_valid():
            deslocamento = form.save(commit=False)
            if not is_admin:
                deslocamento.motorista = user
            deslocamento.save()
            messages.success(request, 'Deslocamento registrado com sucesso!')
            return redirect('frotas:lista_deslocamentos')
    else:
        initial = {}
        trajeto_pk = request.GET.get('trajeto')
        if trajeto_pk:
            trajeto = (
                Trajeto.objects
                .select_related('agendamento__veiculo')
                .filter(pk=trajeto_pk)
                .first()
            )
            if trajeto and (is_admin or trajeto.motorista == user):
                ag = trajeto.agendamento
                if ag and ag.veiculo:
                    initial['veiculo'] = ag.veiculo.pk
                initial['origem'] = trajeto.origem
                initial['destino'] = trajeto.destino
                if trajeto.data_saida:
                    initial['data_hora_saida'] = trajeto.data_saida
                if trajeto.data_chegada:
                    initial['data_hora_chegada'] = trajeto.data_chegada
        form = DeslocamentoForm(motorista=user, is_admin=is_admin, initial=initial)

    return render(
        request,
        'frotas/deslocamentos/form.html',
        {'form': form, 'titulo': 'Registrar Deslocamento'},
    )


@login_required
def detalhe_deslocamento(request, pk):
    deslocamento = get_object_or_404(Deslocamento, pk=pk)
    user = request.user
    is_owner = deslocamento.motorista == user
    if not is_owner and not user.is_administrador() and not user.is_responsavel_campus():
        messages.error(request, 'Acesso não autorizado.')
        return redirect('frotas:lista_deslocamentos')
    return render(
        request,
        'frotas/deslocamentos/detalhe.html',
        {'deslocamento': deslocamento},
    )


@login_required
def editar_deslocamento(request, pk):
    deslocamento = get_object_or_404(Deslocamento, pk=pk)
    user = request.user
    is_admin = user.is_administrador() or user.is_responsavel_campus()
    is_owner = deslocamento.motorista == user

    if not is_owner and not is_admin:
        messages.error(request, 'Acesso não autorizado.')
        return redirect('frotas:lista_deslocamentos')

    if request.method == 'POST':
        form = DeslocamentoForm(
            request.POST, instance=deslocamento,
            motorista=user, is_admin=is_admin,
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Deslocamento atualizado!')
            return redirect('frotas:detalhe_deslocamento', pk=pk)
    else:
        form = DeslocamentoForm(
            instance=deslocamento, motorista=user, is_admin=is_admin,
        )

    return render(
        request,
        'frotas/deslocamentos/form.html',
        {'form': form, 'titulo': 'Editar Deslocamento', 'deslocamento': deslocamento},
    )


@login_required
def deletar_deslocamento(request, pk):
    deslocamento = get_object_or_404(Deslocamento, pk=pk)
    user = request.user
    is_admin = user.is_administrador() or user.is_responsavel_campus()

    if deslocamento.motorista != user and not is_admin:
        messages.error(request, 'Acesso não autorizado.')
        return redirect('frotas:lista_deslocamentos')

    if request.method == 'POST':
        deslocamento.delete()
        messages.success(request, 'Deslocamento excluído.')
        return redirect('frotas:lista_deslocamentos')

    return render(
        request,
        'frotas/deslocamentos/deletar.html',
        {'deslocamento': deslocamento},
    )


@login_required
def ajax_salvar_deslocamento(request):
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)
    user = request.user
    is_admin = user.is_administrador() or user.is_responsavel_campus()
    form = DeslocamentoForm(request.POST, motorista=user, is_admin=is_admin)
    if form.is_valid():
        deslocamento = form.save(commit=False)
        if not is_admin:
            deslocamento.motorista = user
        deslocamento.save()
        dt_chegada = deslocamento.data_hora_chegada
        return JsonResponse({
            'success': True,
            'id': str(deslocamento.pk),
            'resumo': {
                'veiculo': str(deslocamento.veiculo) if deslocamento.veiculo else '—',
                'origem': deslocamento.origem or '—',
                'destino': deslocamento.destino,
                'saida': deslocamento.data_hora_saida.strftime('%d/%m/%Y %H:%M'),
                'chegada': dt_chegada.strftime('%d/%m/%Y %H:%M') if dt_chegada else '—',
                'km_saida': deslocamento.km_saida,
                'km_chegada': (
                    deslocamento.km_chegada
                    if deslocamento.km_chegada is not None else '—'
                ),
            },
            'proxima': {
                'veiculo_id': str(deslocamento.veiculo.pk) if deslocamento.veiculo else '',
                'km_saida': deslocamento.km_chegada if deslocamento.km_chegada is not None else '',
                'data_hora_saida': dt_chegada.strftime('%Y-%m-%dT%H:%M') if dt_chegada else '',
            },
        })
    return JsonResponse({'success': False, 'errors': form.errors}, status=422)


@login_required
def trajeto_detalhes_json(request, pk):
    trajeto = get_object_or_404(
        Trajeto.objects.select_related(
            'agendamento__veiculo', 'agendamento'
        ),
        pk=pk,
    )
    user = request.user
    is_admin = user.is_administrador() or user.is_responsavel_campus()

    # Motorista só pode consultar trajetos atribuídos a si
    if not is_admin and trajeto.motorista != user:
        return JsonResponse({'erro': 'Acesso não autorizado.'}, status=403)

    agendamento = trajeto.agendamento
    veiculo = agendamento.veiculo

    data_saida = trajeto.data_saida.strftime('%Y-%m-%dT%H:%M') if trajeto.data_saida else ''
    data_chegada = trajeto.data_chegada.strftime('%Y-%m-%dT%H:%M') if trajeto.data_chegada else ''

    return JsonResponse({
        'veiculo_id': str(veiculo.pk),
        'veiculo_texto': f'{veiculo.placa} — {veiculo.marca} {veiculo.modelo}',
        'agendamento_id': str(agendamento.pk),
        'agendamento_texto': str(agendamento),
        'origem': trajeto.origem,
        'destino': trajeto.destino,
        'data_saida': data_saida,
        'data_chegada': data_chegada,
        'km_planejado': trajeto.quilometragem,
    })
