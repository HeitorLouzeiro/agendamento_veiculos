from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from common.decorators import is_administrador
from common.pagination import PaginationHelper

from .forms import CampusForm
from .models import Campus


@login_required
@user_passes_test(is_administrador)
def lista_campi(request):
    campi = Campus.objects.all()
    pagination = PaginationHelper(campi, 10)
    campi_paginados = pagination.get_page(request.GET.get('page'))
    return render(request, 'campus/lista.html', {'campi': campi_paginados})


@login_required
@user_passes_test(is_administrador)
def criar_campus(request):
    if request.method == 'POST':
        form = CampusForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campus criado com sucesso!')
            return redirect('campus:lista')
    else:
        form = CampusForm()
    return render(request, 'campus/form.html', {'form': form, 'titulo': 'Novo Campus'})


@login_required
@user_passes_test(is_administrador)
def editar_campus(request, pk):
    campus = get_object_or_404(Campus, pk=pk)
    if request.method == 'POST':
        form = CampusForm(request.POST, instance=campus)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campus atualizado com sucesso!')
            return redirect('campus:lista')
    else:
        form = CampusForm(instance=campus)
    return render(request, 'campus/form.html', {'form': form, 'titulo': 'Editar Campus', 'campus': campus})


@login_required
@user_passes_test(is_administrador)
def deletar_campus(request, pk):
    campus = get_object_or_404(Campus, pk=pk)
    if request.method == 'POST':
        campus.delete()
        messages.success(request, 'Campus excluído com sucesso!')
        return redirect('campus:lista')
    return render(request, 'campus/deletar.html', {'campus': campus})
