"""
Modelo de Solicitação de Exame
"""
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class StatusSolicitacao(str, Enum):
    """Status da solicitação de exame"""
    PENDENTE = "pendente"
    RESULTADO_ENVIADO = "resultado_enviado"
    EM_ANALISE = "em_analise"
    LAUDADO = "laudado"


class SolicitacaoExame(Base):
    __tablename__ = "solicitacoes_exame"

    id = Column(Integer, primary_key=True)
    consultaId = Column(Integer, ForeignKey("consultas.id"), nullable=False)
    pacienteId = Column(Integer, ForeignKey("pacientes.usuarioId"), nullable=False)
    medicoSolicitante = Column(Integer, ForeignKey("medicos.usuarioId"), nullable=False)
    tipoExame = Column(String, nullable=False)
    descricao = Column(Text)
    status = Column(SQLEnum(StatusSolicitacao), default=StatusSolicitacao.PENDENTE)
    dataSolicitacao = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    consulta = relationship("Consulta", foreign_keys=[consultaId])
    paciente = relationship("Paciente", foreign_keys=[pacienteId])
    medico = relationship("Medico", foreign_keys=[medicoSolicitante])
    resultados = relationship("ResultadoExame", back_populates="solicitacao")

    def __repr__(self):
        return f"<SolicitacaoExame(id={self.id}, tipo={self.tipoExame}, status={self.status})>"
