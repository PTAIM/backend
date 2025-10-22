"""
Service para Sumário de Saúde do Paciente
Feature 3 - Épico 1: Gestão de Perfis
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.gestao_perfis.models.paciente import Paciente
from app.gestao_perfis.models.sumario_saude import SumarioSaude


class PacienteService:
    """Service para gerenciar perfil de pacientes"""
    
    @staticmethod
    def criar_perfil_paciente(
        db: Session,
        usuario_id: int,
        data_nascimento: Optional[str] = None,
        endereco: Optional[str] = None
    ) -> Paciente:
        """Cria perfil do paciente"""
        # Verifica se paciente já existe
        paciente_existente = db.query(Paciente).filter(
            Paciente.usuarioId == usuario_id
        ).first()
        
        if paciente_existente:
            raise ValueError("Perfil de paciente já existe para este usuário")
        
        # Cria perfil paciente
        novo_paciente = Paciente(
            usuarioId=usuario_id,
            dataNascimento=data_nascimento,
            endereco=endereco
        )
        
        db.add(novo_paciente)
        db.commit()
        db.refresh(novo_paciente)
        
        return novo_paciente
    
    @staticmethod
    def atualizar_perfil_paciente(
        db: Session,
        usuario_id: int,
        data_nascimento: Optional[str] = None,
        endereco: Optional[str] = None
    ) -> Paciente:
        """Atualiza perfil do paciente"""
        paciente = db.query(Paciente).filter(Paciente.usuarioId == usuario_id).first()
        
        if not paciente:
            raise ValueError("Paciente não encontrado")
        
        if data_nascimento is not None:
            paciente.dataNascimento = data_nascimento
        if endereco is not None:
            paciente.endereco = endereco
        
        db.commit()
        db.refresh(paciente)
        
        return paciente
    
    @staticmethod
    def buscar_paciente_por_id(db: Session, paciente_id: int) -> Optional[Paciente]:
        """Busca paciente por ID"""
        return db.query(Paciente).filter(Paciente.usuarioId == paciente_id).first()


class SumarioSaudeService:
    """Service para gerenciar sumário de saúde do paciente"""
    
    @staticmethod
    def criar_sumario_saude(
        db: Session,
        paciente_id: int,
        historico_doencas: Optional[str] = None,
        alergias: Optional[str] = None,
        medicacoes: Optional[str] = None
    ) -> SumarioSaude:
        """
        História 3.1: Criar sumário de saúde
        Registra alergias, medicamentos e condições preexistentes
        """
        # Cria sumário
        novo_sumario = SumarioSaude(
            historicoDoencas=historico_doencas,
            alergias=alergias,
            medicacoes=medicacoes
        )
        
        db.add(novo_sumario)
        db.commit()
        db.refresh(novo_sumario)
        
        # Associa ao paciente
        paciente = db.query(Paciente).filter(Paciente.usuarioId == paciente_id).first()
        if paciente:
            paciente.sumarioId = novo_sumario.id
            db.commit()
        
        return novo_sumario
    
    @staticmethod
    def atualizar_sumario_saude(
        db: Session,
        sumario_id: int,
        historico_doencas: Optional[str] = None,
        alergias: Optional[str] = None,
        medicacoes: Optional[str] = None
    ) -> SumarioSaude:
        """
        História 3.1: Atualizar sumário de saúde
        Mantém atualizada a lista de alergias, medicamentos e condições
        """
        sumario = db.query(SumarioSaude).filter(SumarioSaude.id == sumario_id).first()
        
        if not sumario:
            raise ValueError("Sumário de saúde não encontrado")
        
        if historico_doencas is not None:
            sumario.historicoDoencas = historico_doencas
        if alergias is not None:
            sumario.alergias = alergias
        if medicacoes is not None:
            sumario.medicacoes = medicacoes
        
        db.commit()
        db.refresh(sumario)
        
        return sumario
    
    @staticmethod
    def buscar_sumario_por_paciente(db: Session, paciente_id: int) -> Optional[SumarioSaude]:
        """
        História 3.1: Buscar sumário de saúde do paciente
        Permite médico ter contexto clínico rápido durante atendimento
        """
        paciente = db.query(Paciente).filter(Paciente.usuarioId == paciente_id).first()
        
        if not paciente or not paciente.sumarioId:
            return None
        
        return db.query(SumarioSaude).filter(SumarioSaude.id == paciente.sumarioId).first()
    
    @staticmethod
    def buscar_sumario_por_id(db: Session, sumario_id: int) -> Optional[SumarioSaude]:
        """Busca sumário por ID"""
        return db.query(SumarioSaude).filter(SumarioSaude.id == sumario_id).first()
