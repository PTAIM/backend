"""
Models - Gestão de Consultas
"""
from .consulta import Consulta, StatusConsulta
from .log_prontuario import LogProntuario, TipoEvento

__all__ = [
    "Consulta",
    "StatusConsulta",
    "LogProntuario",
    "TipoEvento",
]
