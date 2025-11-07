"""
Modelo de Resultado de Exame
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ResultadoExame(Base):
    __tablename__ = "resultados_exame"

    id = Column(Integer, primary_key=True)
    solicitacaoId = Column(Integer, ForeignKey("solicitacoes_exame.id"), nullable=False)
    dataRealizacao = Column(DateTime, nullable=False)
    nomeLaboratorio = Column(String, nullable=False)
    arquivoUrl = Column(String, nullable=False)  # URL/path do arquivo PDF, imagem, etc
    nomeArquivo = Column(String)
    dataUpload = Column(DateTime, default=datetime.utcnow)
    observacoes = Column(Text)

    # Relacionamentos
    solicitacao = relationship("SolicitacaoExame", back_populates="resultados")
    laudos = relationship(
        "LaudoResultado", back_populates="resultado", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ResultadoExame(id={self.id}, solicitacao={self.solicitacaoId})>"
