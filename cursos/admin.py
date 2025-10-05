from django.contrib import admin
from .models import Curso


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'limite_km_mensal', 'ativo', 'criado_em']
    list_filter = ['ativo', 'criado_em']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['criado_em', 'atualizado_em']
