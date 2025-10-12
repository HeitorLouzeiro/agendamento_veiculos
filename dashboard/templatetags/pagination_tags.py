"""
Template tags para paginação reutilizável.
"""
from django import template

register = template.Library()


@register.inclusion_tag('common/pagination.html', takes_context=True)
def render_pagination(context, page_obj, **kwargs):
    """
    Renderiza paginação com filtros preservados.

    Uso:
        {% load pagination_tags %}
        {% render_pagination agendamentos curso=curso_filter
                             status=status_filter %}
    """
    request = context['request']

    # Obter parâmetros atuais da URL
    current_params = request.GET.copy()

    # Adicionar/atualizar parâmetros passados
    for key, value in kwargs.items():
        if value:
            current_params[key] = value

    # Remover o parâmetro 'page' para reconstruir
    if 'page' in current_params:
        current_params.pop('page')

    # Calcular range de páginas para exibir
    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages

    # Mostrar no máximo 7 páginas por vez
    page_range = []
    if total_pages <= 7:
        page_range = range(1, total_pages + 1)
    else:
        if current_page <= 4:
            page_range = range(1, 6)
        elif current_page >= total_pages - 3:
            page_range = range(total_pages - 4, total_pages + 1)
        else:
            page_range = range(current_page - 2, current_page + 3)

    return {
        'page_obj': page_obj,
        'page_range': page_range,
        'query_params': current_params.urlencode(),
        'show_first': current_page > 4 and total_pages > 7,
        'show_last': current_page < total_pages - 3 and total_pages > 7,
    }


@register.simple_tag
def url_replace(request, **kwargs):
    """
    Substitui ou adiciona parâmetros na URL atual.

    Uso:
        <a href="?{% url_replace request page=2 %}">Página 2</a>
    """
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value
        elif key in params:
            del params[key]
    return params.urlencode()
