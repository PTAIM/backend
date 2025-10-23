"""
Schemas Pydantic para Gestão de Perfis
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


# ========== Enums para validação ==========

class TipoUsuarioEnum(str, Enum):
    """Tipos de usuário disponíveis"""
    PACIENTE = "paciente"
    MEDICO = "medico"
    ADMIN = "admin"


class DiaSemanaEnum(str, Enum):
    """Dias da semana"""
    SEGUNDA = "Segunda"
    TERCA = "Terça"
    QUARTA = "Quarta"
    QUINTA = "Quinta"
    SEXTA = "Sexta"
    SABADO = "Sábado"
    DOMINGO = "Domingo"


# ========== Schemas de Request ==========

class CadastroUsuarioRequest(BaseModel):
    nome: str = Field(..., description="Nome completo do usuário", min_length=3)
    email: EmailStr = Field(..., description="Email válido")
    senha: str = Field(..., description="Senha (máximo 72 caracteres)", min_length=6, max_length=72)
    cpf: str = Field(..., description="CPF (apenas números)", min_length=11, max_length=11)
    tipo: TipoUsuarioEnum = Field(..., description="Tipo de usuário")
    telefone: Optional[str] = Field(None, description="Telefone (opcional)")

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "João Silva",
                "email": "joao@email.com",
                "senha": "senha123",
                "cpf": "12345678900",
                "tipo": "paciente",
                "telefone": "11999999999"
            }
        }


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email do usuário")
    senha: str = Field(..., description="Senha", max_length=72)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "joao@email.com",
                "senha": "senha123"
            }
        }


class CriarPerfilMedicoRequest(BaseModel):
    usuario_id: int = Field(..., description="ID do usuário")
    crm: str = Field(..., description="CRM do médico")
    biografia: Optional[str] = Field(None, description="Biografia profissional")
    duracao_consulta: Optional[float] = Field(None, description="Duração padrão da consulta em minutos")
    link_sala_virtual: Optional[str] = Field(None, description="Link da sala virtual para teleconsultas")

    class Config:
        json_schema_extra = {
            "example": {
                "usuario_id": 1,
                "crm": "12345-SP",
                "biografia": "Médico cardiologista com 10 anos de experiência",
                "duracao_consulta": 30.0,
                "link_sala_virtual": "https://meet.google.com/abc-defg-hij"
            }
        }


class AtualizarPerfilMedicoRequest(BaseModel):
    biografia: Optional[str] = Field(None, description="Biografia profissional")
    duracao_consulta: Optional[float] = Field(None, description="Duração padrão da consulta em minutos")
    link_sala_virtual: Optional[str] = Field(None, description="Link da sala virtual")

    class Config:
        json_schema_extra = {
            "example": {
                "biografia": "Médico cardiologista especializado em arritmias",
                "duracao_consulta": 45.0,
                "link_sala_virtual": "https://meet.google.com/xyz-abcd-efg"
            }
        }


class AdicionarEspecialidadeRequest(BaseModel):
    especialidade_id: int = Field(..., description="ID da especialidade")


class CriarEspecialidadeRequest(BaseModel):
    nome: str = Field(..., description="Nome da especialidade", min_length=3)

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "Cardiologia"
            }
        }


class CriarPerfilPacienteRequest(BaseModel):
    usuario_id: int = Field(..., description="ID do usuário")
    data_nascimento: Optional[str] = Field(None, description="Data de nascimento (YYYY-MM-DD)")
    endereco: Optional[str] = Field(None, description="Endereço completo")

    class Config:
        json_schema_extra = {
            "example": {
                "usuario_id": 2,
                "data_nascimento": "1990-05-15",
                "endereco": "Rua das Flores, 123 - São Paulo/SP"
            }
        }


class CriarSumarioSaudeRequest(BaseModel):
    historico_doencas: Optional[str] = Field(None, description="Histórico de doenças preexistentes")
    alergias: Optional[str] = Field(None, description="Lista de alergias")
    medicacoes: Optional[str] = Field(None, description="Medicamentos de uso contínuo")

    class Config:
        json_schema_extra = {
            "example": {
                "historico_doencas": "Hipertensão, Diabetes tipo 2",
                "alergias": "Penicilina, Frutos do mar",
                "medicacoes": "Losartana 50mg, Metformina 850mg"
            }
        }


class AtualizarSumarioSaudeRequest(BaseModel):
    historico_doencas: Optional[str] = Field(None, description="Histórico de doenças")
    alergias: Optional[str] = Field(None, description="Lista de alergias")
    medicacoes: Optional[str] = Field(None, description="Medicamentos de uso contínuo")


# ========== Schemas de Response ==========

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    tipo: str

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class TokenData(BaseModel):
    """Schema para dados do token JWT"""
    sub: Optional[str] = None
    email: Optional[str] = None
    tipo: Optional[str] = None


class MedicoResponse(BaseModel):
    usuario_id: int
    crm: str
    biografia: Optional[str]
    duracao_consulta: Optional[float]
    link_sala_virtual: Optional[str]

    class Config:
        from_attributes = True
