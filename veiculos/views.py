from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from common.constants import VEICULOS_POR_PAGINA
from common.decorators import is_responsavel_ou_admin
from common.pagination import PaginationHelper

from .forms import VeiculoForm
from .models import Veiculo


@login_required
@user_passes_test(is_responsavel_ou_admin)
def lista_veiculos(request):
    is_admin = request.user.is_administrador()
    veiculos = Veiculo.objects.select_related('campus').order_by(
        'campus__nome', 'marca', 'modelo', 'placa'
    )
    if not is_admin:
        veiculos = veiculos.filter(campus=request.user.campus)

    pagination = PaginationHelper(veiculos, VEICULOS_POR_PAGINA)
    veiculos_paginados = pagination.get_page(request.GET.get('page'))

    return render(
        request,
        'veiculos/lista.html',
        {'veiculos': veiculos_paginados, 'is_admin': is_admin}
    )


@login_required
@user_passes_test(is_responsavel_ou_admin)
def criar_veiculo(request):
    campus_fixo = (
        None if request.user.is_administrador() else request.user.campus
    )

    if request.method == 'POST':
        form = VeiculoForm(request.POST, campus_fixo=campus_fixo)
        if form.is_valid():
            veiculo = form.save(commit=False)
            if campus_fixo:
                veiculo.campus = campus_fixo
            veiculo.save()
            messages.success(request, 'Veículo criado com sucesso!')
            return redirect('veiculos:lista')
    else:
        form = VeiculoForm(campus_fixo=campus_fixo)

    context = {'form': form, 'titulo': 'Novo Veículo'}
    return render(request, 'veiculos/form.html', context)


@login_required
@user_passes_test(is_responsavel_ou_admin)
def editar_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    campus_fixo = (
        None if request.user.is_administrador() else request.user.campus
    )

    if not request.user.is_administrador() and veiculo.campus != campus_fixo:
        messages.error(request, 'Você não tem acesso a este veículo.')
        return redirect('veiculos:lista')

    if request.method == 'POST':
        form = VeiculoForm(
            request.POST, instance=veiculo, campus_fixo=campus_fixo
        )
        if form.is_valid():
            veiculo = form.save(commit=False)
            if campus_fixo:
                veiculo.campus = campus_fixo
            veiculo.save()
            messages.success(request, 'Veículo atualizado com sucesso!')
            return redirect('veiculos:lista')
    else:
        form = VeiculoForm(instance=veiculo, campus_fixo=campus_fixo)

    context = {
        'form': form,
        'titulo': 'Editar Veículo',
        'veiculo': veiculo,
    }
    return render(request, 'veiculos/form.html', context)


@login_required
@user_passes_test(is_responsavel_ou_admin)
def deletar_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)

    if (not request.user.is_administrador()
            and veiculo.campus != request.user.campus):
        messages.error(request, 'Você não tem acesso a este veículo.')
        return redirect('veiculos:lista')

    if request.method == 'POST':
        veiculo.delete()
        messages.success(request, 'Veículo deletado com sucesso!')
        return redirect('veiculos:lista')

    return render(request, 'veiculos/deletar.html', {'veiculo': veiculo})
