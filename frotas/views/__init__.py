from .deslocamento_views import (  # noqa: F401
    ajax_salvar_deslocamento,
    criar_deslocamento,
    deletar_deslocamento,
    detalhe_deslocamento,
    editar_deslocamento,
    lista_deslocamentos,
    trajeto_detalhes_json,
)
from .abastecimento_views import (  # noqa: F401
    criar_abastecimento,
    deletar_abastecimento,
    detalhe_abastecimento,
    editar_abastecimento,
    lista_abastecimentos,
)
from .boletim_views import (  # noqa: F401
    boletim_diario,
    dashboard_motorista,
    dashboard_responsavel,
    exportar_boletim_pdf,
)
from .ocorrencia_views import (  # noqa: F401
    criar_ocorrencia,
    deletar_ocorrencia,
    detalhe_ocorrencia,
    editar_ocorrencia,
    lista_ocorrencias,
    resolver_ocorrencia,
)
