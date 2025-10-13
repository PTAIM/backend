# ========== Schemas Pydantic ==========
import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from sqlalchemy import DateTime, UUID
from app.gestao_perfis.models.usuario import TipoUsuario


class UsuarioBase(BaseModel):
    """Schema base para Usuario"""
    nome_completo: str = Field(..., min_length=3, max_length=255, description="Nome completo do usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    cpf: str = Field(..., min_length=11, max_length=11, description="CPF do usuário (apenas números)")
    telefone: Optional[str] = Field(None, min_length=10, max_length=15, description="Telefone do usuário")
    data_nascimento: Optional[DateTime] = Field(None, description="Data de nascimento")
    tipo_usuario: TipoUsuario = Field(..., description="Tipo do usuário")
    foto_perfil_url: Optional[str] = Field(None, max_length=500, description="URL da foto de perfil")

    @field_validator('cpf')
    @classmethod
    def validar_cpf(cls, v: str) -> str:
        """Valida se o CPF contém apenas números"""
        if not v.isdigit():
            raise ValueError('CPF deve conter apenas números')
        if len(v) != 11:
            raise ValueError('CPF deve ter exatamente 11 dígitos')
        return v

    @field_validator('telefone')
    @classmethod
    def validar_telefone(cls, v: Optional[str]) -> Optional[str]:
        """Valida se o telefone contém apenas números"""
        if v is not None and not v.isdigit():
            raise ValueError('Telefone deve conter apenas números')
        return v


class UsuarioCreate(UsuarioBase):
    """Schema para criação de Usuario"""
    senha: str = Field(..., min_length=8, max_length=100, description="Senha do usuário")

    @field_validator('senha')
    @classmethod
    def validar_senha(cls, v: str) -> str:
        """Valida força da senha"""
        if len(v) < 8:
            raise ValueError('Senha deve ter no mínimo 8 caracteres')
        if not any(char.isdigit() for char in v):
            raise ValueError('Senha deve conter pelo menos um número')
        if not any(char.isupper() for char in v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        if not any(char.islower() for char in v):
            raise ValueError('Senha deve conter pelo menos uma letra minúscula')
        return v


class UsuarioUpdate(BaseModel):
    """Schema para atualização de Usuario"""
    nome_completo: Optional[str] = Field(None, min_length=3, max_length=255)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, min_length=10, max_length=15)
    data_nascimento: Optional[DateTime] = None
    foto_perfil_url: Optional[str] = Field(None, max_length=500)
    ativo: Optional[bool] = None

    @field_validator('telefone')
    @classmethod
    def validar_telefone(cls, v: Optional[str]) -> Optional[str]:
        """Valida se o telefone contém apenas números"""
        if v is not None and not v.isdigit():
            raise ValueError('Telefone deve conter apenas números')
        return v


class UsuarioResponse(UsuarioBase):
    """Schema para resposta de Usuario (sem senha)"""
    id: UUID = Field(..., description="ID único do usuário")
    ativo: bool = Field(..., description="Se o usuário está ativo")
    created_at: DateTime = Field(..., description="Data de criação")
    updated_at: Optional[DateTime] = Field(None, description="Data da última atualização")

    model_config = ConfigDict(from_attributes=True)


class UsuarioLogin(BaseModel):
    """Schema para login de Usuario"""
    email: EmailStr = Field(..., description="Email do usuário")
    senha: str = Field(..., description="Senha do usuário")


class UsuarioChangePassword(BaseModel):
    """Schema para alteração de senha"""
    senha_atual: str = Field(..., description="Senha atual do usuário")
    senha_nova: str = Field(..., min_length=8, max_length=100, description="Nova senha do usuário")
    senha_nova_confirmacao: str = Field(..., description="Confirmação da nova senha")

    @field_validator('senha_nova')
    @classmethod
    def validar_senha_nova(cls, v: str) -> str:
        """Valida força da nova senha"""
        if not any(char.isdigit() for char in v):
            raise ValueError('Senha deve conter pelo menos um número')
        if not any(char.isupper() for char in v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        if not any(char.islower() for char in v):
            raise ValueError('Senha deve conter pelo menos uma letra minúscula')
        return v

    def validar_senhas_iguais(self) -> bool:
        """Verifica se as senhas novas são iguais"""
        return self.senha_nova == self.senha_nova_confirmacao
