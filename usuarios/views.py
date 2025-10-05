from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from .forms import RegistroForm


class CustomLoginView(LoginView):
    """View customizada de login"""
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return '/dashboard/'


class CustomLogoutView(LogoutView):
    """View customizada de logout"""
    next_page = 'login'


def registro(request):
    """View para registro de novos professores"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Faz login automático após registro
            messages.success(request, f'Bem-vindo, {user.get_full_name()}! Sua conta foi criada com sucesso.')
            return redirect('dashboard')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})
