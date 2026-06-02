from django.contrib import admin

from .models import Campus


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cidade', 'ativo', 'criado_em']
    list_filter = ['ativo', 'cidade']
    search_fields = ['nome', 'cidade']
