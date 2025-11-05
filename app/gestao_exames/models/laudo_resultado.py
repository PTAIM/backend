"""
Modelo de Relacionamento entre Laudo e Resultado de Exame
"""

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class LaudoResultado(Base):
    __tablename__ = "laudo_resultado"

    id = Column(Integer, primary_key=True)
    laudoId = Column(Integer, ForeignKey("laudos.id"), nullable=False)
    resultadoExameId = Column(
        Integer, ForeignKey("resultados_exame.id"), nullable=False
    )

    # Relacionamentos
    laudo = relationship("Laudo", foreign_keys=[laudoId], back_populates="resultados")
    resultado = relationship(
        "ResultadoExame", foreign_keys=[resultadoExameId], back_populates="laudos"
    )

    def __repr__(self):
        return f"<LaudoResultado(laudoId={self.laudoId}, resultadoId={self.resultadoExameId})>"
