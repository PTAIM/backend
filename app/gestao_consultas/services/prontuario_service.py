"""
Service para Visualização de Prontuário
Feature 2 - Épico 3: Gestão de Exames e Documentação Clínica
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.gestao_consultas.models.log_prontuario import LogProntuario, TipoEvento


class ProntuarioService:
    """Service para visualização do prontuário do paciente"""
    
    @staticmethod
    def visualizar_prontuario(
        db: Session,
        paciente_id: int,
        tipo_evento: Optional[TipoEvento] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None
    ) -> List[LogProntuario]:
        """
        História 2.1: Visualizar prontuário
        Retorna linha do tempo cronológica com eventos de saúde
        com filtros por tipo e data
        """
        query = db.query(LogProntuario).filter(
            LogProntuario.pacienteId == paciente_id
        )
        
        # Filtro por tipo de evento
        if tipo_evento:
            query = query.filter(LogProntuario.tipoEvento == tipo_evento)
        
        # Filtro por período
        if data_inicio:
            query = query.filter(LogProntuario.dataEvento >= data_inicio)
        if data_fim:
            query = query.filter(LogProntuario.dataEvento <= data_fim)
        
        # Ordena por data (mais recente primeiro)
        return query.order_by(LogProntuario.dataEvento.desc()).all()
    
    @staticmethod
    def obter_historico_completo(db: Session, paciente_id: int) -> dict:
        """
        Retorna histórico completo organizado por tipo
        """
        from app.gestao_consultas.models.consulta import Consulta
        from app.gestao_exames.models.solicitacao_exame import SolicitacaoExame
        from app.gestao_exames.models.laudo import Laudo
        
        historico = {
            "consultas": [],
            "exames": [],
            "laudos": [],
            "timeline": []
        }
        
        # Busca consultas
        consultas = db.query(Consulta).filter(
            Consulta.pacienteId == paciente_id
        ).order_by(Consulta.dataHora.desc()).all()
        historico["consultas"] = consultas
        
        # Busca solicitações de exame
        exames = db.query(SolicitacaoExame).filter(
            SolicitacaoExame.pacienteId == paciente_id
        ).order_by(SolicitacaoExame.dataSolicitacao.desc()).all()
        historico["exames"] = exames
        
        # Busca todos os logs para timeline
        timeline = db.query(LogProntuario).filter(
            LogProntuario.pacienteId == paciente_id
        ).order_by(LogProntuario.dataEvento.desc()).all()
        historico["timeline"] = timeline
        
        return historico
    
    @staticmethod
    def contar_eventos_por_tipo(db: Session, paciente_id: int) -> dict:
        """Retorna contagem de eventos por tipo"""
        eventos = db.query(LogProntuario).filter(
            LogProntuario.pacienteId == paciente_id
        ).all()
        
        contagem = {
            TipoEvento.CONSULTA: 0,
            TipoEvento.EXAME: 0,
            TipoEvento.LAUDO: 0,
            TipoEvento.SOLICITACAO_EXAME: 0
        }
        
        for evento in eventos:
            contagem[evento.tipoEvento] += 1
        
        return contagem
