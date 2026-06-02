from django.contrib import admin

from .models import Abastecimento, Ocorrencia


@admin.register(Abastecimento)
class AbastecimentoAdmin(admin.ModelAdmin):
    list_display = ['veiculo', 'motorista', 'data_hora', 'local_posto', 'litros_abastecidos', 'valor_gasto']
    list_filter = ['tipo_combustivel', 'data_hora']
    search_fields = ['veiculo__placa', 'local_posto']
    date_hierarchy = 'data_hora'


@admin.register(Ocorrencia)
class OcorrenciaAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'veiculo', 'gravidade', 'resolvido', 'data_hora']
    list_filter = ['tipo', 'gravidade', 'resolvido']
    search_fields = ['veiculo__placa', 'local', 'descricao']
    date_hierarchy = 'data_hora'
