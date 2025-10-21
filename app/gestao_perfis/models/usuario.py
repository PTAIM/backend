"""
Modelo de Usuario
"""
from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base


class TipoUsuario(str, Enum):
    """Tipos de usuário no sistema"""
    PACIENTE = "paciente"
    MEDICO = "medico"
    ADMIN = "admin"


class Usuario(Base):
    """Modelo de banco de dados para Usuario"""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    telefone = Column(String)
    cpf = Column(String, unique=True)
    hashPassword = Column(String, nullable=False)
    tipo = Column(SQLEnum(TipoUsuario), nullable=False)

    # Relacionamentos
    paciente = relationship("Paciente", back_populates="usuario", uselist=False)
    medico = relationship("Medico", back_populates="usuario", uselist=False)

    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email}, tipo={self.tipo})>"