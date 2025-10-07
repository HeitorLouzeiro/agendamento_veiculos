from django.shortcuts import render


def dashboard(request):
    """Página principal com calendário de agendamentos (público)"""
    return render(request, 'dashboard/index.html')
