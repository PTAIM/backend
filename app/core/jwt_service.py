"""
JWT Service para autenticação com tokens
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Configurações JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sua-chave-secreta-muito-segura-aqui-2024")  # Em produção, use variável de ambiente
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 horas por padrão


class JWTService:
    """Serviço para gerenciar tokens JWT"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Cria um token JWT com os dados fornecidos"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verifica e decodifica um token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[int]:
        """Extrai o ID do usuário do token"""
        payload = JWTService.verify_token(token)
        if payload is None:
            return None
        return payload.get("sub")  # 'sub' é o campo padrão para subject (user ID)