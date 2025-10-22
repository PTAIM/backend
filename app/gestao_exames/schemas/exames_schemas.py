"""
Schemas Pydantic para Gestão de Exames e Laudos
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


# ========== Enums ==========

class StatusSolicitacaoEnum(str, Enum):
    """Status da solicitação de exame"""
    PENDENTE = "pendente"
    RESULTADO_ENVIADO = "resultado_enviado"
    EM_ANALISE = "em_analise"
    LAUDADO = "laudado"


class StatusLaudoEnum(str, Enum):
    """Status do laudo"""
    RASCUNHO = "rascunho"
    FINALIZADO = "finalizado"
    ENVIADO = "enviado"


# ========== Schemas de Request ==========

class CriarSolicitacaoExameRequest(BaseModel):
    consulta_id: int = Field(..., description="ID da consulta")
    paciente_id: int = Field(..., description="ID do paciente")
    medico_id: int = Field(..., description="ID do médico solicitante")
    tipo_exame: str = Field(..., description="Tipo de exame solicitado")
    descricao: Optional[str] = Field(None, description="Descrição ou orientações")

    class Config:
        json_schema_extra = {
            "example": {
                "consulta_id": 1,
                "paciente_id": 2,
                "medico_id": 1,
                "tipo_exame": "Hemograma Completo",
                "descricao": "Solicito hemograma completo com contagem de plaquetas"
            }
        }


class EnviarResultadoExameRequest(BaseModel):
    solicitacao_id: int = Field(..., description="ID da solicitação de exame")
    arquivo_url: str = Field(..., description="URL/caminho do arquivo")
    nome_arquivo: str = Field(..., description="Nome do arquivo")
    observacoes: Optional[str] = Field(None, description="Observações do paciente")

    class Config:
        json_schema_extra = {
            "example": {
                "solicitacao_id": 1,
                "arquivo_url": "/uploads/exames/hemograma_2025.pdf",
                "nome_arquivo": "hemograma_2025.pdf",
                "observacoes": "Exame realizado em jejum de 12h"
            }
        }


class CriarLaudoRequest(BaseModel):
    resultado_exame_id: int = Field(..., description="ID do resultado do exame")
    medico_id: int = Field(..., description="ID do médico que emite o laudo")
    achados: str = Field(..., description="Achados clínicos", min_length=10)
    impressao_diagnostica: str = Field(..., description="Impressão diagnóstica", min_length=10)
    recomendacoes: Optional[str] = Field(None, description="Recomendações")

    class Config:
        json_schema_extra = {
            "example": {
                "resultado_exame_id": 1,
                "medico_id": 1,
                "achados": "Hemograma dentro dos padrões de normalidade. Hemácias: 4.5 milhões/mm³",
                "impressao_diagnostica": "Hemograma normal. Sem alterações significativas.",
                "recomendacoes": "Manter acompanhamento de rotina anual"
            }
        }


class AtualizarLaudoRequest(BaseModel):
    achados: Optional[str] = Field(None, description="Achados clínicos")
    impressao_diagnostica: Optional[str] = Field(None, description="Impressão diagnóstica")
    recomendacoes: Optional[str] = Field(None, description="Recomendações")

    class Config:
        json_schema_extra = {
            "example": {
                "achados": "Hemograma atualizado com novos achados",
                "impressao_diagnostica": "Impressão diagnóstica revisada",
                "recomendacoes": "Novas recomendações adicionadas"
            }
        }


# ========== Schemas de Response ==========

class SolicitacaoExameResponse(BaseModel):
    id: int
    tipo_exame: str
    status: str
    data_solicitacao: datetime

    class Config:
        from_attributes = True


class ResultadoExameResponse(BaseModel):
    id: int
    arquivo_url: str
    nome_arquivo: str
    data_upload: datetime

    class Config:
        from_attributes = True


class LaudoResponse(BaseModel):
    id: int
    medico_id: int
    status: str
    data_emissao: datetime

    class Config:
        from_attributes = True
