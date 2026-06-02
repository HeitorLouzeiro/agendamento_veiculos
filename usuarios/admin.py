from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'campus', 'is_staff', 'is_active',
    ]
    list_filter = ['groups', 'campus', 'is_staff', 'is_superuser', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('campus', 'telefone', 'numero_habilitacao'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {
            'fields': ('campus', 'telefone', 'numero_habilitacao'),
        }),
    )
