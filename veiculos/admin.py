from django.contrib import admin
from .models import Veiculo


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ['placa', 'marca', 'modelo', 'ano', 'ativo', 'criado_em']
    list_filter = ['ativo', 'marca', 'ano']
    search_fields = ['placa', 'modelo', 'marca']
    readonly_fields = ['criado_em', 'atualizado_em']
