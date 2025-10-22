"""
Modelo de Sumário de Saúde
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class SumarioSaude(Base):
    __tablename__ = "sumarios_saude"

    id = Column(Integer, primary_key=True)
    historicoDoencas = Column(String)
    alergias = Column(String)
    medicacoes = Column(String)

    # Relacionamentos
    paciente = relationship("Paciente", back_populates="sumario")

    def __repr__(self):
        return f"<SumarioSaude(id={self.id})>"
