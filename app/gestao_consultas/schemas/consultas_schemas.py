"""
Schemas Pydantic para Gestão de Consultas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


# ========== Enums ==========

class StatusConsultaEnum(str, Enum):
    """Status da consulta"""
    AGENDADA = "agendada"
    CONFIRMADA = "confirmada"
    EM_ANDAMENTO = "em_andamento"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"


class DiaSemanaEnum(str, Enum):
    """Dias da semana"""
    SEGUNDA = "Segunda"
    TERCA = "Terça"
    QUARTA = "Quarta"
    QUINTA = "Quinta"
    SEXTA = "Sexta"
    SABADO = "Sábado"
    DOMINGO = "Domingo"


class TipoEventoEnum(str, Enum):
    """Tipos de eventos no prontuário"""
    CONSULTA = "consulta"
    EXAME = "exame"
    LAUDO = "laudo"
    SOLICITACAO_EXAME = "solicitacao_exame"


# ========== Schemas de Request ==========

class DefinirHorarioAtendimentoRequest(BaseModel):
    medico_id: int = Field(..., description="ID do médico")
    dia_semana: DiaSemanaEnum = Field(..., description="Dia da semana")
    hora: str = Field(..., description="Horário no formato HH:MM", pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")

    class Config:
        json_schema_extra = {
            "example": {
                "medico_id": 1,
                "dia_semana": "Segunda",
                "hora": "14:00"
            }
        }


class AgendarConsultaRequest(BaseModel):
    paciente_id: int = Field(..., description="ID do paciente")
    medico_id: int = Field(..., description="ID do médico")
    data_hora: str = Field(..., description="Data e hora no formato YYYY-MM-DD HH:MM")
    motivo_consulta: Optional[str] = Field(None, description="Motivo da consulta")

    class Config:
        json_schema_extra = {
            "example": {
                "paciente_id": 2,
                "medico_id": 1,
                "data_hora": "2025-11-15 14:00",
                "motivo_consulta": "Consulta de rotina"
            }
        }


class FinalizarConsultaRequest(BaseModel):
    observacoes: Optional[str] = Field(None, description="Observações sobre a consulta")

    class Config:
        json_schema_extra = {
            "example": {
                "observacoes": "Paciente apresentou melhora significativa"
            }
        }


# ========== Schemas de Response ==========

class ConsultaResponse(BaseModel):
    id: int
    paciente_id: int
    medico_id: int
    data_hora: datetime
    status: str
    link_sala_virtual: Optional[str]

    class Config:
        from_attributes = True


class HorarioResponse(BaseModel):
    id: int
    dia_semana: str
    hora: str

    class Config:
        from_attributes = True
