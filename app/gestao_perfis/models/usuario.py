"""
Modelos e Schemas para Usuario
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class TipoUsuario(str, Enum):
    """Tipos de usuário no sistema"""
    PACIENTE = "paciente"
    MEDICO = "medico"
    ADMINISTRADOR = "administrador"
    ATENDENTE = "atendente"


# ========== Modelo SQLAlchemy ==========
class Usuario(Base):
    """Modelo de banco de dados para Usuario"""
    __tablename__ = "usuarios"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    nome_completo = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    cpf = Column(String(11), unique=True, nullable=False, index=True)
    telefone = Column(String(15), nullable=True)
    data_nascimento = Column(DateTime, nullable=True)
    tipo_usuario = Column(SQLEnum(TipoUsuario), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email}, tipo={self.tipo_usuario})>"