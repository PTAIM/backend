"""
Service para Gestão de Laudos
Épico 4: Análise, Diagnóstico e Laudos
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.gestao_exames.models.laudo import Laudo, StatusLaudo
from app.gestao_exames.models.resultado_exame import ResultadoExame
from app.gestao_exames.models.solicitacao_exame import SolicitacaoExame, StatusSolicitacao
from app.gestao_exames.models.laudo_resultado import LaudoResultado
from app.gestao_consultas.models.log_prontuario import LogProntuario, TipoEvento


class LaudoService:
    """Service para gerenciar laudos médicos"""
    
    @staticmethod
    def criar_laudo(
        db: Session,
        paciente_id: int,
        medico_id: int,
        titulo: str,
        descricao: str,
        exames_ids: List[int]
    ) -> Laudo:
        """
        História 2.1 (Épico 4): Emitir laudo médico
        Médico cria laudo associando um ou mais exames
        """
        # Cria laudo
        novo_laudo = Laudo(
            medicoId=medico_id,
            titulo=titulo,
            descricao=descricao,
            status=StatusLaudo.RASCUNHO
        )
        
        db.add(novo_laudo)
        db.flush()  # Para obter o ID
        
        # Associa exames ao laudo
        for exame_id in exames_ids:
            resultado = db.query(ResultadoExame).filter(
                ResultadoExame.id == exame_id
            ).first()
            
            if not resultado:
                raise ValueError(f"Resultado de exame {exame_id} não encontrado")
            
            laudo_resultado = LaudoResultado(
                laudoId=novo_laudo.id,
                resultadoExameId=exame_id
            )
            db.add(laudo_resultado)
        
        db.commit()
        db.refresh(novo_laudo)
        
        return novo_laudo
    
    @staticmethod
    def atualizar_laudo(
        db: Session,
        laudo_id: int,
        titulo: Optional[str] = None,
        descricao: Optional[str] = None
    ) -> Laudo:
        """Atualiza laudo em rascunho"""
        laudo = db.query(Laudo).filter(Laudo.id == laudo_id).first()
        
        if not laudo:
            raise ValueError("Laudo não encontrado")
        
        if laudo.status != StatusLaudo.RASCUNHO:
            raise ValueError("Apenas laudos em rascunho podem ser editados")
        
        if titulo is not None:
            laudo.titulo = titulo
        if descricao is not None:
            laudo.descricao = descricao
        
        db.commit()
        db.refresh(laudo)
        
        return laudo
    
    @staticmethod
    def finalizar_laudo(db: Session, laudo_id: int) -> Laudo:
        """
        História 2.1 (Épico 4): Finalizar laudo
        Marca laudo como finalizado e registra no prontuário
        """
        laudo = db.query(Laudo).filter(Laudo.id == laudo_id).first()
        
        if not laudo:
            raise ValueError("Laudo não encontrado")
        
        laudo.status = StatusLaudo.FINALIZADO
        db.commit()
        db.refresh(laudo)
        
        # Registra no prontuário - busca o paciente do primeiro exame
        laudo_resultado = db.query(LaudoResultado).filter(
            LaudoResultado.laudoId == laudo_id
        ).first()
        
        if laudo_resultado:
            resultado = db.query(ResultadoExame).filter(
                ResultadoExame.id == laudo_resultado.resultadoExameId
            ).first()
            
            if resultado and resultado.solicitacao:
                log = LogProntuario(
                    pacienteId=resultado.solicitacao.pacienteId,
                    tipoEvento=TipoEvento.LAUDO,
                    descricao=f"Laudo médico finalizado: {laudo.titulo}",
                    referenciaId=laudo.id
                )
                db.add(log)
                db.commit()
        
        return laudo
    
    @staticmethod
    def buscar_laudo_por_id(db: Session, laudo_id: int) -> Optional[Laudo]:
        """Busca laudo por ID"""
        return db.query(Laudo).filter(Laudo.id == laudo_id).first()
    
    @staticmethod
    def listar_laudos_medico(
        db: Session, 
        medico_id: int,
        status: Optional[StatusLaudo] = None
    ) -> List[Laudo]:
        """Lista todos os laudos emitidos por um médico"""
        query = db.query(Laudo).filter(Laudo.medicoId == medico_id)
        
        if status:
            query = query.filter(Laudo.status == status)
        
        return query.order_by(Laudo.dataEmissao.desc()).all()
    
    @staticmethod
    def listar_laudos_paciente(
        db: Session, 
        paciente_id: int,
        status: Optional[StatusLaudo] = None
    ) -> List[Laudo]:
        """Lista laudos de um paciente"""
        # Join com laudo_resultado -> resultado_exame -> solicitacao
        query = db.query(Laudo).join(
            LaudoResultado, Laudo.id == LaudoResultado.laudoId
        ).join(
            ResultadoExame, LaudoResultado.resultadoExameId == ResultadoExame.id
        ).join(
            SolicitacaoExame, ResultadoExame.solicitacaoId == SolicitacaoExame.id
        ).filter(
            SolicitacaoExame.pacienteId == paciente_id
        )
        
        if status:
            query = query.filter(Laudo.status == status)
        
        return query.order_by(Laudo.dataEmissao.desc()).all()
