"""
Views para gerenciamento de veículos.

Este módulo contém views para CRUD de veículos,
acessível apenas por administradores.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from common.constants import VEICULOS_POR_PAGINA
from common.decorators import is_administrador
from common.pagination import PaginationHelper

from .forms import VeiculoForm
from .models import Veiculo


@login_required
@user_passes_test(is_administrador)
def lista_veiculos(request):
    """Lista todos os veículos com paginação"""
    veiculos = Veiculo.objects.all().order_by('marca', 'modelo', 'placa')

    # Aplicar paginação
    pagination = PaginationHelper(veiculos, VEICULOS_POR_PAGINA)
    veiculos_paginados = pagination.get_page(request.GET.get('page'))

    return render(
        request,
        'veiculos/lista.html',
        {'veiculos': veiculos_paginados}
    )


@login_required
@user_passes_test(is_administrador)
def criar_veiculo(request):
    """Cria um novo veículo"""
    if request.method == 'POST':
        form = VeiculoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Veículo criado com sucesso!')
            return redirect('veiculos:lista')
    else:
        form = VeiculoForm()

    context = {'form': form, 'titulo': 'Novo Veículo'}
    return render(request, 'veiculos/form.html', context)


@login_required
@user_passes_test(is_administrador)
def editar_veiculo(request, pk):
    """Edita um veículo existente"""
    veiculo = get_object_or_404(Veiculo, pk=pk)

    if request.method == 'POST':
        form = VeiculoForm(request.POST, instance=veiculo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Veículo atualizado com sucesso!')
            return redirect('veiculos:lista')
    else:
        form = VeiculoForm(instance=veiculo)

    context = {
        'form': form,
        'titulo': 'Editar Veículo',
        'veiculo': veiculo
    }
    return render(request, 'veiculos/form.html', context)


@login_required
@user_passes_test(is_administrador)
def deletar_veiculo(request, pk):
    """Deleta um veículo"""
    veiculo = get_object_or_404(Veiculo, pk=pk)

    if request.method == 'POST':
        veiculo.delete()
        messages.success(request, 'Veículo deletado com sucesso!')
        return redirect('veiculos:lista')

    return render(request, 'veiculos/deletar.html', {'veiculo': veiculo})
