"""
Modelo de Laudo Médico
"""

from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class StatusLaudo(str, Enum):
    """Status do laudo"""

    RASCUNHO = "RASCUNHO"
    FINALIZADO = "FINALIZADO"


class Laudo(Base):
    __tablename__ = "laudos"

    id = Column(Integer, primary_key=True)
    medicoId = Column(Integer, ForeignKey("medicos.usuarioId"), nullable=False)
    titulo = Column(String, nullable=False)
    descricao = Column(Text, nullable=False)
    status = Column(SQLEnum(StatusLaudo), default=StatusLaudo.RASCUNHO)
    dataEmissao = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    resultados = relationship(
        "LaudoResultado", back_populates="laudo", cascade="all, delete-orphan"
    )
    medico = relationship("Medico", foreign_keys=[medicoId])

    def __repr__(self):
        return f"<Laudo(id={self.id}, medico={self.medicoId}, status={self.status})>"
