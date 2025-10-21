"""
Service para Gestão de Consultas
Feature 1 e 2 - Épico 2: Ciclo de Vida de Consultas
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.gestao_consultas.models.consulta import Consulta, StatusConsulta
from app.gestao_consultas.models.log_prontuario import LogProntuario, TipoEvento


class ConsultaService:
    """Service para gerenciar consultas"""
    
    @staticmethod
    def agendar_consulta(
        db: Session,
        paciente_id: int,
        medico_id: int,
        data_hora: datetime,
        motivo_consulta: Optional[str] = None
    ) -> Consulta:
        """
        História 1.2: Agendar consulta
        Paciente agenda consulta com médico em horário disponível
        """
        # Verifica se horário está disponível
        consulta_existente = db.query(Consulta).filter(
            Consulta.medicoId == medico_id,
            Consulta.dataHora == data_hora,
            Consulta.status.in_([StatusConsulta.AGENDADA, StatusConsulta.CONFIRMADA])
        ).first()
        
        if consulta_existente:
            raise ValueError("Horário não disponível")
        
        # Busca link da sala virtual do médico
        from app.gestao_perfis.models.medico import Medico
        medico = db.query(Medico).filter(Medico.usuarioId == medico_id).first()
        link_sala = medico.linkSalaVirtual if medico else None
        
        # Cria consulta
        nova_consulta = Consulta(
            pacienteId=paciente_id,
            medicoId=medico_id,
            dataHora=data_hora,
            status=StatusConsulta.AGENDADA,
            motivoConsulta=motivo_consulta,
            linkSalaVirtual=link_sala
        )
        
        db.add(nova_consulta)
        db.commit()
        db.refresh(nova_consulta)
        
        # Registra no prontuário
        ConsultaService._registrar_log_prontuario(
            db, paciente_id, TipoEvento.CONSULTA, nova_consulta.id,
            f"Consulta agendada com médico ID {medico_id}"
        )
        
        return nova_consulta
    
    @staticmethod
    def confirmar_consulta(db: Session, consulta_id: int) -> Consulta:
        """Confirma consulta agendada"""
        consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
        
        if not consulta:
            raise ValueError("Consulta não encontrada")
        
        consulta.status = StatusConsulta.CONFIRMADA
        db.commit()
        db.refresh(consulta)
        
        return consulta
    
    @staticmethod
    def iniciar_consulta(db: Session, consulta_id: int) -> Consulta:
        """
        História 2.1: Iniciar teleconsulta
        Marca consulta como em andamento
        """
        consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
        
        if not consulta:
            raise ValueError("Consulta não encontrada")
        
        consulta.status = StatusConsulta.EM_ANDAMENTO
        db.commit()
        db.refresh(consulta)
        
        return consulta
    
    @staticmethod
    def finalizar_consulta(
        db: Session,
        consulta_id: int,
        observacoes: Optional[str] = None
    ) -> Consulta:
        """Finaliza consulta"""
        consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
        
        if not consulta:
            raise ValueError("Consulta não encontrada")
        
        consulta.status = StatusConsulta.FINALIZADA
        if observacoes:
            consulta.observacoes = observacoes
        
        db.commit()
        db.refresh(consulta)
        
        return consulta
    
    @staticmethod
    def cancelar_consulta(db: Session, consulta_id: int) -> Consulta:
        """Cancela consulta"""
        consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
        
        if not consulta:
            raise ValueError("Consulta não encontrada")
        
        consulta.status = StatusConsulta.CANCELADA
        db.commit()
        db.refresh(consulta)
        
        return consulta
    
    @staticmethod
    def listar_consultas_paciente(
        db: Session,
        paciente_id: int,
        apenas_futuras: bool = False
    ) -> List[Consulta]:
        """
        História 1.3: Visualizar consultas do paciente
        Lista consultas futuras e/ou passadas
        """
        query = db.query(Consulta).filter(Consulta.pacienteId == paciente_id)
        
        if apenas_futuras:
            query = query.filter(Consulta.dataHora >= datetime.now())
        
        return query.order_by(Consulta.dataHora.desc()).all()
    
    @staticmethod
    def listar_consultas_medico(
        db: Session,
        medico_id: int,
        apenas_futuras: bool = False
    ) -> List[Consulta]:
        """
        História 1.3: Visualizar consultas do médico
        Lista consultas futuras e/ou passadas
        """
        query = db.query(Consulta).filter(Consulta.medicoId == medico_id)
        
        if apenas_futuras:
            query = query.filter(Consulta.dataHora >= datetime.now())
        
        return query.order_by(Consulta.dataHora.desc()).all()
    
    @staticmethod
    def buscar_consulta_por_id(db: Session, consulta_id: int) -> Optional[Consulta]:
        """Busca consulta por ID"""
        return db.query(Consulta).filter(Consulta.id == consulta_id).first()
    
    @staticmethod
    def _registrar_log_prontuario(
        db: Session,
        paciente_id: int,
        tipo_evento: TipoEvento,
        referencia_id: int,
        descricao: str
    ):
        """Registra evento no prontuário do paciente"""
        log = LogProntuario(
            pacienteId=paciente_id,
            tipoEvento=tipo_evento,
            descricao=descricao,
            referenciaId=referencia_id
        )
        db.add(log)
        db.commit()
