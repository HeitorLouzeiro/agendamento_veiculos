"""
Views para gerenciamento de cursos.

Este módulo contém views para CRUD de cursos,
acessível apenas por administradores.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from common.constants import CURSOS_POR_PAGINA
from common.decorators import is_administrador
from common.pagination import PaginationHelper

from .forms import CursoForm
from .models import Curso


@login_required
@user_passes_test(is_administrador)
def lista_cursos(request):
    """Lista todos os cursos com paginação"""
    cursos = Curso.objects.all().order_by('nome')

    # Aplicar paginação
    pagination = PaginationHelper(cursos, CURSOS_POR_PAGINA)
    cursos_paginados = pagination.get_page(request.GET.get('page'))

    return render(
        request,
        'cursos/lista.html',
        {'cursos': cursos_paginados}
    )


@login_required
@user_passes_test(is_administrador)
def criar_curso(request):
    """Cria um novo curso"""
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Curso criado com sucesso!')
            return redirect('cursos:lista')
    else:
        form = CursoForm()

    context = {'form': form, 'titulo': 'Novo Curso'}
    return render(request, 'cursos/form.html', context)


@login_required
@user_passes_test(is_administrador)
def editar_curso(request, pk):
    """Edita um curso existente"""
    curso = get_object_or_404(Curso, pk=pk)

    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            messages.success(request, 'Curso atualizado com sucesso!')
            return redirect('cursos:lista')
    else:
        form = CursoForm(instance=curso)

    context = {'form': form, 'titulo': 'Editar Curso', 'curso': curso}
    return render(request, 'cursos/form.html', context)


@login_required
@user_passes_test(is_administrador)
def deletar_curso(request, pk):
    """Deleta um curso"""
    curso = get_object_or_404(Curso, pk=pk)

    if request.method == 'POST':
        curso.delete()
        messages.success(request, 'Curso deletado com sucesso!')
        return redirect('cursos:lista')

    return render(request, 'cursos/deletar.html', {'curso': curso})
