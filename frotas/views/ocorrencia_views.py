from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from common.pagination import PaginationHelper

from ..forms import OcorrenciaForm
from ..models import Ocorrencia


@login_required
def lista_ocorrencias(request):
    user = request.user
    if user.is_administrador() or user.is_responsavel_campus():
        qs = Ocorrencia.objects.select_related(
            'veiculo', 'motorista', 'agendamento'
        )
    else:
        qs = Ocorrencia.objects.filter(
            motorista=user
        ).select_related('veiculo', 'agendamento')

    pagination = PaginationHelper(qs, 10)
    ocorrencias = pagination.get_page(request.GET.get('page'))
    return render(
        request,
        'frotas/ocorrencias/lista.html',
        {'ocorrencias': ocorrencias},
    )


@login_required
def criar_ocorrencia(request):
    user = request.user
    is_admin = user.is_administrador() or user.is_responsavel_campus()

    if request.method == 'POST':
        form = OcorrenciaForm(
            request.POST, motorista=user, is_admin=is_admin
        )
        if form.is_valid():
            ocorrencia = form.save(commit=False)
            ocorrencia.veiculo = ocorrencia.agendamento.veiculo
            if not is_admin:
                ocorrencia.motorista = user
            ocorrencia.save()
            messages.success(request, 'Ocorrência registrada com sucesso!')
            return redirect('frotas:lista_ocorrencias')
    else:
        form = OcorrenciaForm(motorista=user, is_admin=is_admin)

    return render(
        request,
        'frotas/ocorrencias/form.html',
        {'form': form, 'titulo': 'Registrar Ocorrência'},
    )


@login_required
def detalhe_ocorrencia(request, pk):
    ocorrencia = get_object_or_404(Ocorrencia, pk=pk)
    user = request.user
    is_owner = ocorrencia.motorista == user
    if not is_owner and not user.is_administrador() and not user.is_responsavel_campus():
        messages.error(request, 'Acesso não autorizado.')
        return redirect('frotas:lista_ocorrencias')
    return render(
        request,
        'frotas/ocorrencias/detalhe.html',
        {'ocorrencia': ocorrencia},
    )


@login_required
def editar_ocorrencia(request, pk):
    ocorrencia = get_object_or_404(Ocorrencia, pk=pk)
    user = request.user
    is_admin = user.is_administrador() or user.is_responsavel_campus()
    is_owner = ocorrencia.motorista == user

    if not is_owner and not is_admin:
        messages.error(request, 'Acesso não autorizado.')
        return redirect('frotas:lista_ocorrencias')

    if request.method == 'POST':
        form = OcorrenciaForm(
            request.POST, instance=ocorrencia,
            motorista=user, is_admin=is_admin,
        )
        if form.is_valid():
            ocorrencia = form.save(commit=False)
            ocorrencia.veiculo = ocorrencia.agendamento.veiculo
            ocorrencia.save()
            messages.success(request, 'Ocorrência atualizada!')
            return redirect('frotas:detalhe_ocorrencia', pk=pk)
    else:
        form = OcorrenciaForm(
            instance=ocorrencia, motorista=user, is_admin=is_admin
        )

    return render(
        request,
        'frotas/ocorrencias/form.html',
        {'form': form, 'titulo': 'Editar Ocorrência', 'ocorrencia': ocorrencia},
    )


@login_required
def deletar_ocorrencia(request, pk):
    ocorrencia = get_object_or_404(Ocorrencia, pk=pk)
    user = request.user
    is_admin = user.is_administrador() or user.is_responsavel_campus()

    if ocorrencia.motorista != user and not is_admin:
        messages.error(request, 'Acesso não autorizado.')
        return redirect('frotas:lista_ocorrencias')

    if request.method == 'POST':
        ocorrencia.delete()
        messages.success(request, 'Ocorrência excluída.')
        return redirect('frotas:lista_ocorrencias')

    return render(
        request,
        'frotas/ocorrencias/deletar.html',
        {'ocorrencia': ocorrencia},
    )


@login_required
def resolver_ocorrencia(request, pk):
    ocorrencia = get_object_or_404(Ocorrencia, pk=pk)
    user = request.user
    if not user.is_administrador() and not user.is_responsavel_campus():
        messages.error(request, 'Acesso não autorizado.')
        return redirect('frotas:lista_ocorrencias')

    if request.method == 'POST':
        ocorrencia.resolvido = True
        ocorrencia.save()
        messages.success(request, 'Ocorrência marcada como resolvida.')
    return redirect('frotas:detalhe_ocorrencia', pk=pk)
