from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Curso
from .forms import CursoForm


def is_administrador(user):
    """Verifica se o usuário é administrador"""
    return user.is_administrador()


@login_required
@user_passes_test(is_administrador)
def lista_cursos(request):
    """Lista todos os cursos"""
    cursos = Curso.objects.all()
    return render(request, 'cursos/lista.html', {'cursos': cursos})


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
    
    return render(request, 'cursos/form.html', {'form': form, 'titulo': 'Novo Curso'})


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
    
    return render(request, 'cursos/form.html', {'form': form, 'titulo': 'Editar Curso', 'curso': curso})


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
