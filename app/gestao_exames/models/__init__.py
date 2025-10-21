"""
Models - Gestão de Exames
"""
from .solicitacao_exame import SolicitacaoExame, StatusSolicitacao
from .resultado_exame import ResultadoExame
from .laudo import Laudo, StatusLaudo

__all__ = [
    "SolicitacaoExame",
    "StatusSolicitacao",
    "ResultadoExame",
    "Laudo",
    "StatusLaudo",
]
