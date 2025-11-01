"""
Modelo de Solicitação de Exame
"""
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from nanoid import generate

from app.core.database import Base


class StatusSolicitacao(str, Enum):
    """Status da solicitação de exame"""
    AGUARDANDO_RESULTADO = "AGUARDANDO_RESULTADO"
    RESULTADO_ENVIADO = "RESULTADO_ENVIADO"
    CANCELADO = "CANCELADO"


def gerar_codigo_solicitacao():
    """Gera um código único de 10 caracteres para a solicitação"""
    return generate(size=10)


class SolicitacaoExame(Base):
    __tablename__ = "solicitacoes_exame"

    id = Column(Integer, primary_key=True)
    codigoSolicitacao = Column(String, unique=True, nullable=False, default=gerar_codigo_solicitacao)
    consultaId = Column(Integer, ForeignKey("consultas.id"), nullable=True)  # Pode ser opcional
    pacienteId = Column(Integer, ForeignKey("pacientes.usuarioId"), nullable=False)
    medicoSolicitante = Column(Integer, ForeignKey("medicos.usuarioId"), nullable=False)
    nomeExame = Column(String, nullable=False)
    hipoteseDiagnostica = Column(Text)
    detalhesPreparo = Column(Text)
    status = Column(SQLEnum(StatusSolicitacao), default=StatusSolicitacao.AGUARDANDO_RESULTADO)
    dataSolicitacao = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    consulta = relationship("Consulta", foreign_keys=[consultaId])
    paciente = relationship("Paciente", foreign_keys=[pacienteId])
    medico = relationship("Medico", foreign_keys=[medicoSolicitante])
    resultados = relationship("ResultadoExame", back_populates="solicitacao")

    def __repr__(self):
        return f"<SolicitacaoExame(id={self.id}, nomeExame={self.nomeExame}, status={self.status})>"
