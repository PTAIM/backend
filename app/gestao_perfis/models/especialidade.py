"""
Modelo de Especialidade
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Especialidade(Base):
    __tablename__ = "especialidades"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)

    # Relacionamentos
    medicos = relationship("MedicoEspecialidade", back_populates="especialidade")

    def __repr__(self):
        return f"<Especialidade(id={self.id}, nome={self.nome})>"
