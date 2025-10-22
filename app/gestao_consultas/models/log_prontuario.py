"""
Modelo de Log do Prontuário
"""
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class TipoEvento(str, Enum):
    """Tipos de eventos no prontuário"""
    CONSULTA = "consulta"
    EXAME = "exame"
    LAUDO = "laudo"
    SOLICITACAO_EXAME = "solicitacao_exame"


class LogProntuario(Base):
    __tablename__ = "logs_prontuario"

    id = Column(Integer, primary_key=True)
    pacienteId = Column(Integer, ForeignKey("pacientes.usuarioId"), nullable=False)
    tipoEvento = Column(SQLEnum(TipoEvento), nullable=False)
    dataEvento = Column(DateTime, default=datetime.utcnow)
    descricao = Column(Text)
    referenciaId = Column(Integer)  # ID da consulta, exame, laudo, etc
    
    # Relacionamentos
    paciente = relationship("Paciente", foreign_keys=[pacienteId])

    def __repr__(self):
        return f"<LogProntuario(id={self.id}, tipo={self.tipoEvento}, paciente={self.pacienteId})>"
