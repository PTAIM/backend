"""
Modelo de Paciente
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    usuarioId = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    dataNascimento = Column(String)
    endereco = Column(String)
    sumarioId = Column(Integer, ForeignKey("sumarios_saude.id"))

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="paciente")
    sumario = relationship("SumarioSaude", back_populates="paciente")

    def __repr__(self):
        return f"<Paciente(usuarioId={self.usuarioId})>"
