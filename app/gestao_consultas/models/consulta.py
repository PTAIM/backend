"""
Modelo de Consulta
"""
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class StatusConsulta(str, Enum):
    """Status da consulta"""
    AGENDADA = "agendada"
    CONFIRMADA = "confirmada"
    EM_ANDAMENTO = "em_andamento"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"


class Consulta(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True)
    pacienteId = Column(Integer, ForeignKey("pacientes.usuarioId"), nullable=False)
    medicoId = Column(Integer, ForeignKey("medicos.usuarioId"), nullable=False)
    dataHora = Column(DateTime, nullable=False)
    status = Column(SQLEnum(StatusConsulta), default=StatusConsulta.AGENDADA)
    motivoConsulta = Column(Text)
    observacoes = Column(Text)
    linkSalaVirtual = Column(String)
    
    # Relacionamentos
    paciente = relationship("Paciente", foreign_keys=[pacienteId])
    medico = relationship("Medico", foreign_keys=[medicoId])

    def __repr__(self):
        return f"<Consulta(id={self.id}, paciente={self.pacienteId}, medico={self.medicoId}, status={self.status})>"
