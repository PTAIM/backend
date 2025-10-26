"""
Schemas Pydantic para Gestão de Exames e Laudos
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ========== Enums ==========

class StatusSolicitacaoEnum(str, Enum):
    """Status da solicitação de exame"""
    AGUARDANDO_RESULTADO = "AGUARDANDO_RESULTADO"
    RESULTADO_ENVIADO = "RESULTADO_ENVIADO"
    CANCELADO = "CANCELADO"


class StatusLaudoEnum(str, Enum):
    """Status do laudo"""
    RASCUNHO = "RASCUNHO"
    FINALIZADO = "FINALIZADO"


# ========== Schemas de Request ==========

class CriarSolicitacaoExameRequest(BaseModel):
    paciente_id: int = Field(..., description="ID do paciente")
    nome_exame: str = Field(..., description="Nome do exame solicitado")
    hipotese_diagnostica: Optional[str] = Field(None, description="Hipótese diagnóstica")
    detalhes_preparo: Optional[str] = Field(None, description="Detalhes de preparo para o exame")

    class Config:
        json_schema_extra = {
            "example": {
                "paciente_id": 2,
                "nome_exame": "Hemograma Completo",
                "hipotese_diagnostica": "Anemia ferropriva",
                "detalhes_preparo": "Jejum de 12 horas"
            }
        }


class EnviarResultadoExameRequest(BaseModel):
    codigo_solicitacao: str = Field(..., description="Código UUID da solicitação")
    data_realizacao: datetime = Field(..., description="Data de realização do exame")
    nome_laboratorio: str = Field(..., description="Nome do laboratório")
    observacoes: Optional[str] = Field(None, description="Observações do exame")
    # arquivos serão tratados separadamente via upload

    class Config:
        json_schema_extra = {
            "example": {
                "codigo_solicitacao": "550e8400-e29b-41d4-a716-446655440000",
                "data_realizacao": "2025-10-26T10:00:00",
                "nome_laboratorio": "Laboratório São Lucas",
                "observacoes": "Exame realizado em jejum de 12h"
            }
        }


class CriarLaudoRequest(BaseModel):
    paciente_id: int = Field(..., description="ID do paciente")
    titulo: str = Field(..., description="Título do laudo", min_length=3)
    descricao: str = Field(..., description="Descrição do laudo", min_length=10)
    exames_ids: List[int] = Field(..., description="Lista de IDs de exames a incluir no laudo")

    class Config:
        json_schema_extra = {
            "example": {
                "paciente_id": 2,
                "titulo": "Laudo de Hemograma Completo",
                "descricao": "Análise detalhada do hemograma apresentando valores dentro dos padrões normais...",
                "exames_ids": [1, 2]
            }
        }


class AtualizarLaudoRequest(BaseModel):
    titulo: Optional[str] = Field(None, description="Título do laudo")
    descricao: Optional[str] = Field(None, description="Descrição do laudo")

    class Config:
        json_schema_extra = {
            "example": {
                "titulo": "Laudo Atualizado",
                "descricao": "Descrição atualizada do laudo"
            }
        }


class AtualizarStatusSolicitacaoRequest(BaseModel):
    status: StatusSolicitacaoEnum = Field(..., description="Novo status da solicitação")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "CANCELADO"
            }
        }


# ========== Schemas de Response ==========

class ExameResponse(BaseModel):
    id: int
    solicitacao_id: int
    codigo_solicitacao: str
    nome_exame: str
    data_realizacao: datetime
    nome_laboratorio: str
    nome_arquivo: Optional[str]
    url_arquivo: str

    class Config:
        from_attributes = True


class SolicitacaoExameResponse(BaseModel):
    id: int
    codigo_solicitacao: str
    paciente_id: int
    paciente_nome: str
    paciente_cpf: str
    medico_id: int
    medico_nome: str
    medico_crm: str
    nome_exame: str
    hipotese_diagnostica: Optional[str]
    detalhes_preparo: Optional[str]
    status: str
    data_solicitacao: datetime

    class Config:
        from_attributes = True


class LaudoResponse(BaseModel):
    id: int
    paciente_id: int
    paciente_nome: str
    paciente_cpf: str
    medico_id: int
    medico_nome: str
    medico_crm: str
    titulo: str
    descricao: str
    status: str
    data_emissao: datetime
    exames: List[ExameResponse]

    class Config:
        from_attributes = True
