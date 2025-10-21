"""
Modelo de relacionamento Médico-Especialidade
"""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class MedicoEspecialidade(Base):
    __tablename__ = "medico_especialidades"

    medicoId = Column(Integer, ForeignKey("medicos.usuarioId"), primary_key=True)
    especialidadeId = Column(Integer, ForeignKey("especialidades.id"), primary_key=True)

    # Relacionamentos
    medico = relationship("Medico", back_populates="especialidades")
    especialidade = relationship("Especialidade", back_populates="medicos")

    def __repr__(self):
        return f"<MedicoEspecialidade(medicoId={self.medicoId}, especialidadeId={self.especialidadeId})>"
