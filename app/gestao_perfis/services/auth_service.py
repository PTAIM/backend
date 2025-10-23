"""
Service para Autenticação e Cadastro
Feature 1 - Épico 1: Gestão de Perfis
"""
from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import bcrypt
from datetime import timedelta

from app.gestao_perfis.models.usuario import Usuario, TipoUsuario
from app.core.jwt_service import JWTService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service para gerenciar autenticação e cadastro de usuários"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Gera hash da senha usando bcrypt diretamente"""
        # Bcrypt tem limite de 72 bytes
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha corresponde ao hash"""
        # Bcrypt tem limite de 72 bytes
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    @staticmethod
    def cadastrar_usuario(
        db: Session,
        nome: str,
        email: str,
        senha: str,
        cpf: str,
        tipo: TipoUsuario,
        telefone: Optional[str] = None
    ) -> Usuario:
        """
        História 1.1: Cadastro de usuário
        Cria um novo usuário no sistema com senha hasheada
        """
        # Verifica se email já existe
        usuario_existente = db.query(Usuario).filter(Usuario.email == email).first()
        if usuario_existente:
            raise ValueError("Email já cadastrado")
        
        # Verifica se CPF já existe
        cpf_existente = db.query(Usuario).filter(Usuario.cpf == cpf).first()
        if cpf_existente:
            raise ValueError("CPF já cadastrado")
        
        # Cria novo usuário
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            hashPassword=AuthService.hash_password(senha),
            cpf=cpf,
            tipo=tipo,
            telefone=telefone
        )
        
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        
        return novo_usuario
    
    @staticmethod
    def fazer_login(db: Session, email: str, senha: str) -> Optional[Usuario]:
        """
        História 1.1: Login de usuário
        Autentica usuário e retorna seus dados se credenciais válidas
        """
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        
        if not usuario:
            return None
        
        if not AuthService.verify_password(senha, usuario.hashPassword):
            return None
        
        return usuario
    
    @staticmethod
    def buscar_usuario_por_id(db: Session, usuario_id: int) -> Optional[Usuario]:
        """Busca usuário por ID"""
        return db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    @staticmethod
    def buscar_usuario_por_email(db: Session, email: str) -> Optional[Usuario]:
        """Busca usuário por email"""
        return db.query(Usuario).filter(Usuario.email == email).first()
    
    @staticmethod
    def criar_token_acesso(usuario: Usuario) -> str:
        """Cria token JWT para o usuário"""
        data = {
            "sub": str(usuario.id),
            "email": usuario.email,
            "tipo": usuario.tipo.value,
            "nome": usuario.nome
        }
        return JWTService.create_access_token(data=data)
    
    @staticmethod
    def verificar_token(token: str) -> Optional[dict]:
        """Verifica se o token é válido"""
        return JWTService.verify_token(token)
