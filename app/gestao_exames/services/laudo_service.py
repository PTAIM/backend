"""
Service para Gestão de Laudos
Épico 4: Análise, Diagnóstico e Laudos
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.gestao_exames.models.laudo import Laudo, StatusLaudo
from app.gestao_exames.models.resultado_exame import ResultadoExame
from app.gestao_exames.models.solicitacao_exame import SolicitacaoExame, StatusSolicitacao
from app.gestao_consultas.models.log_prontuario import LogProntuario, TipoEvento


class LaudoService:
    """Service para gerenciar laudos médicos"""
    
    @staticmethod
    def obter_fila_trabalho(db: Session, medico_id: int) -> List[ResultadoExame]:
        """
        História 1.1 (Épico 4): Fila de trabalho / Caixa de entrada
        Retorna exames pendentes de análise para o médico
        """
        # Busca solicitações que o médico fez e que já têm resultado
        solicitacoes = db.query(SolicitacaoExame).filter(
            SolicitacaoExame.medicoSolicitante == medico_id,
            SolicitacaoExame.status.in_([
                StatusSolicitacao.RESULTADO_ENVIADO,
                StatusSolicitacao.EM_ANALISE
            ])
        ).all()
        
        resultados_pendentes = []
        for solicitacao in solicitacoes:
            resultados = db.query(ResultadoExame).filter(
                ResultadoExame.solicitacaoId == solicitacao.id
            ).all()
            
            for resultado in resultados:
                # Verifica se já tem laudo finalizado
                laudo_existente = db.query(Laudo).filter(
                    Laudo.resultadoExameId == resultado.id,
                    Laudo.status.in_([StatusLaudo.FINALIZADO, StatusLaudo.ENVIADO])
                ).first()
                
                if not laudo_existente:
                    resultados_pendentes.append(resultado)
        
        return resultados_pendentes
    
    @staticmethod
    def criar_laudo(
        db: Session,
        resultado_exame_id: int,
        medico_id: int,
        achados: str,
        impressao_diagnostica: str,
        recomendacoes: Optional[str] = None
    ) -> Laudo:
        """
        História 2.1 (Épico 4): Emitir laudo médico
        Médico redige laudo estruturado com achados e impressão diagnóstica
        """
        # Verifica se resultado existe
        resultado = db.query(ResultadoExame).filter(
            ResultadoExame.id == resultado_exame_id
        ).first()
        
        if not resultado:
            raise ValueError("Resultado de exame não encontrado")
        
        # Cria laudo
        novo_laudo = Laudo(
            resultadoExameId=resultado_exame_id,
            medicoId=medico_id,
            achados=achados,
            impressaoDiagnostica=impressao_diagnostica,
            recomendacoes=recomendacoes,
            status=StatusLaudo.RASCUNHO
        )
        
        db.add(novo_laudo)
        
        # Atualiza status da solicitação
        resultado.solicitacao.status = StatusSolicitacao.EM_ANALISE
        
        db.commit()
        db.refresh(novo_laudo)
        
        return novo_laudo
    
    @staticmethod
    def atualizar_laudo(
        db: Session,
        laudo_id: int,
        achados: Optional[str] = None,
        impressao_diagnostica: Optional[str] = None,
        recomendacoes: Optional[str] = None
    ) -> Laudo:
        """Atualiza laudo em rascunho"""
        laudo = db.query(Laudo).filter(Laudo.id == laudo_id).first()
        
        if not laudo:
            raise ValueError("Laudo não encontrado")
        
        if laudo.status != StatusLaudo.RASCUNHO:
            raise ValueError("Apenas laudos em rascunho podem ser editados")
        
        if achados is not None:
            laudo.achados = achados
        if impressao_diagnostica is not None:
            laudo.impressaoDiagnostica = impressao_diagnostica
        if recomendacoes is not None:
            laudo.recomendacoes = recomendacoes
        
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
        
        # Atualiza status da solicitação
        resultado = db.query(ResultadoExame).filter(
            ResultadoExame.id == laudo.resultadoExameId
        ).first()
        
        if resultado:
            resultado.solicitacao.status = StatusSolicitacao.LAUDADO
        
        db.commit()
        db.refresh(laudo)
        
        # Registra no prontuário
        if resultado:
            log = LogProntuario(
                pacienteId=resultado.solicitacao.pacienteId,
                tipoEvento=TipoEvento.LAUDO,
                descricao=f"Laudo médico finalizado: {resultado.solicitacao.tipoExame}",
                referenciaId=laudo.id
            )
            db.add(log)
            db.commit()
        
        return laudo
    
    @staticmethod
    def enviar_laudo(db: Session, laudo_id: int) -> Laudo:
        """Envia laudo ao paciente"""
        laudo = db.query(Laudo).filter(Laudo.id == laudo_id).first()
        
        if not laudo:
            raise ValueError("Laudo não encontrado")
        
        if laudo.status != StatusLaudo.FINALIZADO:
            raise ValueError("Apenas laudos finalizados podem ser enviados")
        
        laudo.status = StatusLaudo.ENVIADO
        db.commit()
        db.refresh(laudo)
        
        return laudo
    
    @staticmethod
    def buscar_laudo_por_id(db: Session, laudo_id: int) -> Optional[Laudo]:
        """Busca laudo por ID"""
        return db.query(Laudo).filter(Laudo.id == laudo_id).first()
    
    @staticmethod
    def listar_laudos_medico(db: Session, medico_id: int) -> List[Laudo]:
        """Lista todos os laudos emitidos por um médico"""
        return db.query(Laudo).filter(
            Laudo.medicoId == medico_id
        ).order_by(Laudo.dataEmissao.desc()).all()
    
    @staticmethod
    def buscar_laudos_por_resultado(db: Session, resultado_exame_id: int) -> List[Laudo]:
        """Busca laudos de um resultado de exame"""
        return db.query(Laudo).filter(
            Laudo.resultadoExameId == resultado_exame_id
        ).all()
