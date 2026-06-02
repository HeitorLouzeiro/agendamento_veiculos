from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from common.pagination import PaginationHelper

from ..forms import AbastecimentoForm
from ..models import Abastecimento


@login_required
def lista_abastecimentos(request):
    user = request.user
    if user.is_administrador() or user.is_responsavel_campus():
        qs = Abastecimento.objects.select_related(
            'veiculo', 'motorista', 'agendamento'
        )
    else:
        qs = Abastecimento.objects.filter(
            motorista=user
        ).select_related('veiculo', 'agendamento')

    pagination = PaginationHelper(qs, 10)
    abastecimentos = pagination.get_page(request.GET.get('page'))
    return render(
        request,
        'frotas/abastecimentos/lista.html',
        {'abastecimentos': abastecimentos},
    )


@login_required
def criar_abastecimento(request):
    user = request.user
    is_admin = user.is_administrador() or user.is_responsavel_campus()

    if request.method == 'POST':
        form = AbastecimentoForm(
            request.POST, motorista=user, is_admin=is_admin
        )
        if form.is_valid():
            abastecimento = form.save(commit=False)
            if not is_admin:
                abastecimento.motorista = user
            abastecimento.save()
            messages.success(request, 'Abastecimento registrado com sucesso!')
            return redirect('frotas:lista_abastecimentos')
    else:
        form = AbastecimentoForm(motorista=user, is_admin=is_admin)

    return render(
        request,
        'frotas/abastecimentos/form.html',
        {'form': form, 'titulo': 'Registrar Abastecimento'},
    )


@login_required
def detalhe_abastecimento(request, pk):
    abastecimento = get_object_or_404(Abastecimento, pk=pk)
    user = request.user
    is_owner = abastecimento.motorista == user
    if not is_owner and not user.is_administrador() and not user.is_responsavel_campus():
        messages.error(request, 'Acesso não autorizado.')
        return redirect('frotas:lista_abastecimentos')
    return render(
        request,
        'frotas/abastecimentos/detalhe.html',
        {'abastecimento': abastecimento},
    )


@login_required
def editar_abastecimento(request, pk):
    abastecimento = get_object_or_404(Abastecimento, pk=pk)
    user = request.user
    is_admin = user.is_administrador() or user.is_responsavel_campus()
    is_owner = abastecimento.motorista == user

    if not is_owner and not is_admin:
        messages.error(request, 'Acesso não autorizado.')
        return redirect('frotas:lista_abastecimentos')

    if request.method == 'POST':
        form = AbastecimentoForm(
            request.POST, instance=abastecimento,
            motorista=user, is_admin=is_admin,
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Abastecimento atualizado!')
            return redirect('frotas:detalhe_abastecimento', pk=pk)
    else:
        form = AbastecimentoForm(
            instance=abastecimento, motorista=user, is_admin=is_admin
        )

    return render(
        request,
        'frotas/abastecimentos/form.html',
        {'form': form, 'titulo': 'Editar Abastecimento', 'abastecimento': abastecimento},
    )


@login_required
def deletar_abastecimento(request, pk):
    abastecimento = get_object_or_404(Abastecimento, pk=pk)
    user = request.user
    is_admin = user.is_administrador() or user.is_responsavel_campus()

    if abastecimento.motorista != user and not is_admin:
        messages.error(request, 'Acesso não autorizado.')
        return redirect('frotas:lista_abastecimentos')

    if request.method == 'POST':
        abastecimento.delete()
        messages.success(request, 'Abastecimento excluído.')
        return redirect('frotas:lista_abastecimentos')

    return render(
        request,
        'frotas/abastecimentos/deletar.html',
        {'abastecimento': abastecimento},
    )
