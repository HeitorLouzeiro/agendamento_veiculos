from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from common.constants import CURSOS_POR_PAGINA
from common.decorators import is_responsavel_ou_admin
from common.pagination import PaginationHelper

from .forms import CursoForm
from .models import Curso


@login_required
@user_passes_test(is_responsavel_ou_admin)
def lista_cursos(request):
    is_admin = request.user.is_administrador()
    cursos = Curso.objects.select_related('campus').order_by(
        'campus__nome', 'nome'
    )
    if not is_admin:
        cursos = cursos.filter(campus=request.user.campus)

    pagination = PaginationHelper(cursos, CURSOS_POR_PAGINA)
    cursos_paginados = pagination.get_page(request.GET.get('page'))

    return render(
        request,
        'cursos/lista.html',
        {'cursos': cursos_paginados, 'is_admin': is_admin}
    )


@login_required
@user_passes_test(is_responsavel_ou_admin)
def criar_curso(request):
    campus_fixo = (
        None if request.user.is_administrador() else request.user.campus
    )

    if request.method == 'POST':
        form = CursoForm(request.POST, campus_fixo=campus_fixo)
        if form.is_valid():
            curso = form.save(commit=False)
            if campus_fixo:
                curso.campus = campus_fixo
            curso.save()
            messages.success(request, 'Curso criado com sucesso!')
            return redirect('cursos:lista')
    else:
        form = CursoForm(campus_fixo=campus_fixo)

    context = {'form': form, 'titulo': 'Novo Curso'}
    return render(request, 'cursos/form.html', context)


@login_required
@user_passes_test(is_responsavel_ou_admin)
def editar_curso(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    campus_fixo = (
        None if request.user.is_administrador() else request.user.campus
    )

    if not request.user.is_administrador() and curso.campus != campus_fixo:
        messages.error(request, 'Você não tem acesso a este curso.')
        return redirect('cursos:lista')

    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso, campus_fixo=campus_fixo)
        if form.is_valid():
            curso = form.save(commit=False)
            if campus_fixo:
                curso.campus = campus_fixo
            curso.save()
            messages.success(request, 'Curso atualizado com sucesso!')
            return redirect('cursos:lista')
    else:
        form = CursoForm(instance=curso, campus_fixo=campus_fixo)

    context = {'form': form, 'titulo': 'Editar Curso', 'curso': curso}
    return render(request, 'cursos/form.html', context)


@login_required
@user_passes_test(is_responsavel_ou_admin)
def deletar_curso(request, pk):
    curso = get_object_or_404(Curso, pk=pk)

    if not request.user.is_administrador() and curso.campus != request.user.campus:
        messages.error(request, 'Você não tem acesso a este curso.')
        return redirect('cursos:lista')

    if request.method == 'POST':
        curso.delete()
        messages.success(request, 'Curso deletado com sucesso!')
        return redirect('cursos:lista')

    return render(request, 'cursos/deletar.html', {'curso': curso})
