"""
Modelo de Médico
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Medico(Base):
    __tablename__ = "medicos"

    usuarioId = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    crm = Column(String, nullable=False)
    biografia = Column(String)
    duracaoConsulta = Column(Float)
    linkSalaVirtual = Column(String)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="medico")
    especialidades = relationship("MedicoEspecialidade", back_populates="medico")
    agendas = relationship("Agenda", back_populates="medico")

    def __repr__(self):
        return f"<Medico(usuarioId={self.usuarioId}, crm={self.crm})>"
