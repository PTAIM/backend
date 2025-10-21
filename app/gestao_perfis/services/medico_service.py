"""
Service para Perfil do Médico
Feature 2 - Épico 1: Gestão de Perfis
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.gestao_perfis.models.medico import Medico
from app.gestao_perfis.models.especialidade import Especialidade
from app.gestao_perfis.models.medico_especialidade import MedicoEspecialidade


class MedicoService:
    """Service para gerenciar perfil de médicos"""
    
    @staticmethod
    def criar_perfil_medico(
        db: Session,
        usuario_id: int,
        crm: str,
        biografia: Optional[str] = None,
        duracao_consulta: Optional[float] = None,
        link_sala_virtual: Optional[str] = None
    ) -> Medico:
        """
        História 2.1: Criar/preencher perfil do médico
        Cria perfil médico com biografia, especialidades e dados profissionais
        """
        # Verifica se médico já existe
        medico_existente = db.query(Medico).filter(Medico.usuarioId == usuario_id).first()
        if medico_existente:
            raise ValueError("Perfil de médico já existe para este usuário")
        
        # Cria perfil médico
        novo_medico = Medico(
            usuarioId=usuario_id,
            crm=crm,
            biografia=biografia,
            duracaoConsulta=duracao_consulta,
            linkSalaVirtual=link_sala_virtual
        )
        
        db.add(novo_medico)
        db.commit()
        db.refresh(novo_medico)
        
        return novo_medico
    
    @staticmethod
    def atualizar_perfil_medico(
        db: Session,
        usuario_id: int,
        biografia: Optional[str] = None,
        duracao_consulta: Optional[float] = None,
        link_sala_virtual: Optional[str] = None
    ) -> Medico:
        """
        História 2.1: Atualizar perfil do médico
        Atualiza informações do perfil médico
        """
        medico = db.query(Medico).filter(Medico.usuarioId == usuario_id).first()
        
        if not medico:
            raise ValueError("Médico não encontrado")
        
        if biografia is not None:
            medico.biografia = biografia
        if duracao_consulta is not None:
            medico.duracaoConsulta = duracao_consulta
        if link_sala_virtual is not None:
            medico.linkSalaVirtual = link_sala_virtual
        
        db.commit()
        db.refresh(medico)
        
        return medico
    
    @staticmethod
    def adicionar_especialidade(
        db: Session,
        medico_id: int,
        especialidade_id: int
    ) -> MedicoEspecialidade:
        """
        História 2.1: Adicionar especialidade ao médico
        Associa uma especialidade ao perfil do médico
        """
        # Verifica se associação já existe
        associacao_existente = db.query(MedicoEspecialidade).filter(
            MedicoEspecialidade.medicoId == medico_id,
            MedicoEspecialidade.especialidadeId == especialidade_id
        ).first()
        
        if associacao_existente:
            raise ValueError("Especialidade já associada ao médico")
        
        # Cria associação
        nova_associacao = MedicoEspecialidade(
            medicoId=medico_id,
            especialidadeId=especialidade_id
        )
        
        db.add(nova_associacao)
        db.commit()
        db.refresh(nova_associacao)
        
        return nova_associacao
    
    @staticmethod
    def remover_especialidade(
        db: Session,
        medico_id: int,
        especialidade_id: int
    ) -> bool:
        """Remove especialidade do médico"""
        associacao = db.query(MedicoEspecialidade).filter(
            MedicoEspecialidade.medicoId == medico_id,
            MedicoEspecialidade.especialidadeId == especialidade_id
        ).first()
        
        if not associacao:
            return False
        
        db.delete(associacao)
        db.commit()
        
        return True
    
    @staticmethod
    def buscar_medico_por_id(db: Session, medico_id: int) -> Optional[Medico]:
        """Busca médico por ID"""
        return db.query(Medico).filter(Medico.usuarioId == medico_id).first()
    
    @staticmethod
    def buscar_medicos_por_especialidade(
        db: Session,
        especialidade_id: int
    ) -> List[Medico]:
        """
        História 2.1: Buscar médicos por especialidade
        Permite pacientes encontrarem médicos pela especialidade
        """
        medicos_especialidade = db.query(MedicoEspecialidade).filter(
            MedicoEspecialidade.especialidadeId == especialidade_id
        ).all()
        
        medicos = []
        for me in medicos_especialidade:
            medico = db.query(Medico).filter(Medico.usuarioId == me.medicoId).first()
            if medico:
                medicos.append(medico)
        
        return medicos
    
    @staticmethod
    def listar_todos_medicos(db: Session) -> List[Medico]:
        """Lista todos os médicos"""
        return db.query(Medico).all()


class EspecialidadeService:
    """Service para gerenciar especialidades médicas"""
    
    @staticmethod
    def criar_especialidade(db: Session, nome: str) -> Especialidade:
        """Cria nova especialidade"""
        especialidade_existente = db.query(Especialidade).filter(
            Especialidade.nome == nome
        ).first()
        
        if especialidade_existente:
            raise ValueError("Especialidade já existe")
        
        nova_especialidade = Especialidade(nome=nome)
        db.add(nova_especialidade)
        db.commit()
        db.refresh(nova_especialidade)
        
        return nova_especialidade
    
    @staticmethod
    def listar_especialidades(db: Session) -> List[Especialidade]:
        """Lista todas as especialidades"""
        return db.query(Especialidade).all()
    
    @staticmethod
    def buscar_especialidade_por_id(db: Session, especialidade_id: int) -> Optional[Especialidade]:
        """Busca especialidade por ID"""
        return db.query(Especialidade).filter(Especialidade.id == especialidade_id).first()
