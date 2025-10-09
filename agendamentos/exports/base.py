"""
Classe base para exportadores de relatórios.

Define interface comum para todos os exportadores.
"""

from abc import ABC, abstractmethod


class BaseExporter(ABC):
    """
    Classe base abstrata para exportadores de relatórios.
    """

    def __init__(self, dados):
        """
        Inicializa o exportador.

        Args:
            dados: Dados a serem exportados
        """
        self.dados = dados

    @abstractmethod
    def exportar(self):
        """
        Exporta os dados no formato específico.

        Returns:
            Objeto de resposta apropriado para o formato
        """
        pass

    @abstractmethod
    def get_content_type(self):
        """Retorna o content-type apropriado."""
        pass

    @abstractmethod
    def get_filename(self):
        """Retorna o nome do arquivo."""
        pass
