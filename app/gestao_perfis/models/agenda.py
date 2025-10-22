"""
Modelo de Agenda
"""
from enum import Enum
from sqlalchemy import Column, Integer, Time, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base


class DiaSemana(str, Enum):
    """Dias da semana"""
    SEGUNDA = "Segunda"
    TERCA = "Terça"
    QUARTA = "Quarta"
    QUINTA = "Quinta"
    SEXTA = "Sexta"
    SABADO = "Sábado"
    DOMINGO = "Domingo"


class Agenda(Base):
    __tablename__ = "agendas"

    id = Column(Integer, primary_key=True)
    medicoId = Column(Integer, ForeignKey("medicos.usuarioId"))
    diaSemana = Column(SQLEnum(DiaSemana))
    hora = Column(Time)

    # Relacionamentos
    medico = relationship("Medico", back_populates="agendas")

    def __repr__(self):
        return f"<Agenda(id={self.id}, medicoId={self.medicoId}, diaSemana={self.diaSemana})>"
