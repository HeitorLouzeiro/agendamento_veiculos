from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from .models import Agendamento, Trajeto
from .forms import AgendamentoForm, TrajetoFormSet


def is_administrador(user):
    """Verifica se o usuário é administrador"""
    return user.is_administrador()


@login_required
def lista_agendamentos(request):
    """Lista agendamentos do usuário (ou todos se admin)"""
    if request.user.is_administrador():
        agendamentos = Agendamento.objects.all().select_related('curso', 'professor', 'veiculo')
    else:
        agendamentos = Agendamento.objects.filter(professor=request.user).select_related('curso', 'veiculo')
    
    # Filtros
    status = request.GET.get('status')
    if status:
        agendamentos = agendamentos.filter(status=status)
    
    curso_id = request.GET.get('curso')
    if curso_id:
        agendamentos = agendamentos.filter(curso_id=curso_id)
    
    return render(request, 'agendamentos/lista.html', {
        'agendamentos': agendamentos,
        'status_filter': status,
        'curso_filter': curso_id,
    })


@login_required
def criar_agendamento(request):
    """Cria um novo agendamento"""
    if request.method == 'POST':
        form = AgendamentoForm(request.POST, user=request.user)
        formset = TrajetoFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    agendamento = form.save(commit=False)
                    agendamento.professor = request.user
                    agendamento.status = 'pendente'
                    agendamento.save()
                    
                    # Salva os trajetos
                    formset.instance = agendamento
                    formset.save()
                    
                    # Valida limite de KM se for aprovação automática (não aplicável aqui)
                    # A validação será feita na aprovação
                    
                    messages.success(request, 'Agendamento criado com sucesso! Aguarde a aprovação do administrador.')
                    return redirect('agendamentos:lista')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = AgendamentoForm(user=request.user)
        formset = TrajetoFormSet()
    
    return render(request, 'agendamentos/form.html', {
        'form': form,
        'formset': formset,
        'titulo': 'Novo Agendamento'
    })


@login_required
def editar_agendamento(request, pk):
    """Edita um agendamento existente"""
    agendamento = get_object_or_404(Agendamento, pk=pk)
    
    # Verifica permissão: apenas o professor dono ou admin pode editar
    if not request.user.is_administrador() and agendamento.professor != request.user:
        messages.error(request, 'Você não tem permissão para editar este agendamento.')
        return redirect('agendamentos:lista')
    
    # Não permite editar agendamentos aprovados ou reprovados (apenas pendentes)
    if agendamento.status != 'pendente':
        messages.warning(request, 'Apenas agendamentos pendentes podem ser editados.')
        return redirect('agendamentos:lista')
    
    if request.method == 'POST':
        form = AgendamentoForm(request.POST, instance=agendamento, user=request.user)
        formset = TrajetoFormSet(request.POST, instance=agendamento)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    agendamento = form.save()
                    formset.save()
                    
                    messages.success(request, 'Agendamento atualizado com sucesso!')
                    return redirect('agendamentos:lista')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = AgendamentoForm(instance=agendamento, user=request.user)
        formset = TrajetoFormSet(instance=agendamento)
    
    return render(request, 'agendamentos/form.html', {
        'form': form,
        'formset': formset,
        'titulo': 'Editar Agendamento',
        'agendamento': agendamento
    })


@login_required
def detalhe_agendamento(request, pk):
    """Exibe detalhes de um agendamento"""
    agendamento = get_object_or_404(Agendamento, pk=pk)
    
    # Verifica permissão
    if not request.user.is_administrador() and agendamento.professor != request.user:
        messages.error(request, 'Você não tem permissão para ver este agendamento.')
        return redirect('agendamentos:lista')
    
    trajetos = agendamento.trajetos.all()
    total_km = agendamento.get_total_km()
    
    return render(request, 'agendamentos/detalhe.html', {
        'agendamento': agendamento,
        'trajetos': trajetos,
        'total_km': total_km
    })


@login_required
def deletar_agendamento(request, pk):
    """Deleta um agendamento"""
    agendamento = get_object_or_404(Agendamento, pk=pk)
    
    # Verifica permissão
    if not request.user.is_administrador() and agendamento.professor != request.user:
        messages.error(request, 'Você não tem permissão para deletar este agendamento.')
        return redirect('agendamentos:lista')
    
    # Não permite deletar agendamentos aprovados
    if agendamento.status == 'aprovado':
        messages.warning(request, 'Agendamentos aprovados não podem ser deletados.')
        return redirect('agendamentos:lista')
    
    if request.method == 'POST':
        agendamento.delete()
        messages.success(request, 'Agendamento deletado com sucesso!')
        return redirect('agendamentos:lista')
    
    return render(request, 'agendamentos/deletar.html', {'agendamento': agendamento})


@login_required
@user_passes_test(is_administrador)
def aprovacao_agendamentos(request):
    """Lista agendamentos pendentes para aprovação"""
    agendamentos_pendentes = Agendamento.objects.filter(
        status='pendente'
    ).select_related('curso', 'professor', 'veiculo').order_by('data_inicio')
    
    return render(request, 'agendamentos/aprovacao.html', {
        'agendamentos': agendamentos_pendentes
    })


@login_required
@user_passes_test(is_administrador)
def aprovar_agendamento(request, pk):
    """Aprova um agendamento"""
    agendamento = get_object_or_404(Agendamento, pk=pk)
    
    if request.method == 'POST':
        try:
            agendamento.aprovar()
            messages.success(request, f'Agendamento aprovado com sucesso!')
            return redirect('agendamentos:aprovacao')
        except ValidationError as e:
            messages.error(request, f'Erro ao aprovar agendamento: {e}')
            return redirect('agendamentos:aprovacao')
    
    return redirect('agendamentos:aprovacao')


@login_required
@user_passes_test(is_administrador)
def reprovar_agendamento(request, pk):
    """Reprova um agendamento"""
    agendamento = get_object_or_404(Agendamento, pk=pk)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '')
        if not motivo:
            messages.error(request, 'É necessário informar o motivo da reprovação.')
            return redirect('agendamentos:aprovacao')
        
        agendamento.reprovar(motivo)
        messages.success(request, 'Agendamento reprovado.')
        return redirect('agendamentos:aprovacao')
    
    return render(request, 'agendamentos/reprovar.html', {'agendamento': agendamento})


@login_required
def agendamentos_json(request):
    """Retorna agendamentos em formato JSON para o calendário"""
    if request.user.is_administrador():
        agendamentos = Agendamento.objects.all()
    else:
        agendamentos = Agendamento.objects.filter(professor=request.user)
    
    eventos = []
    for agendamento in agendamentos:
        # Define cor baseada no status
        if agendamento.status == 'pendente':
            color = '#ffc107'  # Amarelo
        elif agendamento.status == 'aprovado':
            color = '#28a745'  # Verde
        else:  # reprovado
            color = '#dc3545'  # Vermelho
        
        eventos.append({
            'id': agendamento.id,
            'title': f"{agendamento.curso.nome} - {agendamento.veiculo.placa}",
            'start': agendamento.data_inicio.isoformat(),
            'end': agendamento.data_fim.isoformat(),
            'color': color,
            'url': f'/agendamentos/{agendamento.id}/',
        })
    
    return JsonResponse(eventos, safe=False)
