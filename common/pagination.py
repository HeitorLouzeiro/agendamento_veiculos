"""
Utilitários para paginação.

Este módulo fornece uma classe helper para facilitar e padronizar
a paginação em todo o projeto.
"""

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


class PaginationHelper:
    """
    Helper para simplificar a paginação de querysets.

    Uso:
        pagination = PaginationHelper(queryset, per_page=10)
        page_obj = pagination.get_page(request.GET.get('page'))
    """

    def __init__(self, queryset, per_page=10):
        """
        Inicializa o helper de paginação.

        Args:
            queryset: QuerySet do Django a ser paginado
            per_page: Número de itens por página (padrão: 10)
        """
        self.paginator = Paginator(queryset, per_page)

    def get_page(self, page_number):
        """
        Retorna a página solicitada, tratando erros automaticamente.

        Args:
            page_number: Número da página solicitada

        Returns:
            Page: Objeto Page do Django com os itens da página
        """
        try:
            return self.paginator.page(page_number)
        except PageNotAnInteger:
            # Se não é um inteiro, retorna a primeira página
            return self.paginator.page(1)
        except EmptyPage:
            # Se está fora do range, retorna a última página
            return self.paginator.page(self.paginator.num_pages)

    @property
    def num_pages(self):
        """Retorna o número total de páginas."""
        return self.paginator.num_pages

    @property
    def count(self):
        """Retorna o número total de itens."""
        return self.paginator.count
