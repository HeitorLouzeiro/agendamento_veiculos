from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Veiculo
from .forms import VeiculoForm


def is_administrador(user):
    """Verifica se o usuário é administrador"""
    return user.is_administrador()


@login_required
@user_passes_test(is_administrador)
def lista_veiculos(request):
    """Lista todos os veículos"""
    veiculos = Veiculo.objects.all()
    return render(request, 'veiculos/lista.html', {'veiculos': veiculos})


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
    
    return render(request, 'veiculos/form.html', {'form': form, 'titulo': 'Novo Veículo'})


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
    
    return render(request, 'veiculos/form.html', {'form': form, 'titulo': 'Editar Veículo', 'veiculo': veiculo})


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
