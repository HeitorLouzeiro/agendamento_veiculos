from django.contrib import admin
from .models import Agendamento, Trajeto


class TrajetoInline(admin.TabularInline):
    model = Trajeto
    extra = 1
    fields = ['origem', 'destino', 'data_saida', 'data_chegada', 'quilometragem', 'descricao']


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ['curso', 'professor', 'veiculo', 'data_inicio', 'data_fim', 'status', 'get_total_km']
    list_filter = ['status', 'curso', 'data_inicio']
    search_fields = ['curso__nome', 'professor__username', 'veiculo__placa']
    readonly_fields = ['criado_em', 'atualizado_em']
    inlines = [TrajetoInline]
    
    def get_total_km(self, obj):
        return f"{obj.get_total_km()} km"
    get_total_km.short_description = 'Total KM'


@admin.register(Trajeto)
class TrajetoAdmin(admin.ModelAdmin):
    list_display = ['agendamento', 'origem', 'destino', 'data_saida', 'quilometragem']
    list_filter = ['data_saida']
    search_fields = ['origem', 'destino', 'agendamento__curso__nome']
