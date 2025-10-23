"""
Dependencies de Autenticação para FastAPI
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.gestao_perfis.services.auth_service import AuthService
from app.gestao_perfis.models.usuario import Usuario

# Configuração do HTTPBearer para tokens JWT
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependency para obter o usuário atual através do token JWT
    Usado para proteger rotas que requerem autenticação
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verifica o token
        token = credentials.credentials
        payload = AuthService.verificar_token(token)
        
        if payload is None:
            raise credentials_exception
        
        # Extrai o ID do usuário do token
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Busca o usuário no banco
        usuario = AuthService.buscar_usuario_por_id(db, int(user_id))
        if usuario is None:
            raise credentials_exception
        
        return usuario
        
    except Exception:
        raise credentials_exception


def get_current_active_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """
    Dependency para obter usuário ativo
    Pode ser estendida para verificar se conta está ativa, bloqueada, etc.
    """
    # Aqui você pode adicionar validações extras como:
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user


def require_medico(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Dependency que exige que o usuário seja um médico"""
    if current_user.tipo.value != "medico":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a médicos"
        )
    return current_user


def require_paciente(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Dependency que exige que o usuário seja um paciente"""
    if current_user.tipo.value != "paciente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a pacientes"
        )
    return current_user


def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Dependency que exige que o usuário seja um administrador"""
    if current_user.tipo.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    return current_user