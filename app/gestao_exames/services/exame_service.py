"""
Service para Gestão de Exames
Épico 3: Gestão de Exames e Documentação Clínica
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.gestao_exames.models.solicitacao_exame import SolicitacaoExame, StatusSolicitacao
from app.gestao_exames.models.resultado_exame import ResultadoExame
from app.gestao_consultas.models.log_prontuario import LogProntuario, TipoEvento


class ExameService:
    """Service para gerenciar solicitações e resultados de exames"""
    
    @staticmethod
    def criar_solicitacao_exame(
        db: Session,
        paciente_id: int,
        medico_id: int,
        nome_exame: str,
        hipotese_diagnostica: Optional[str] = None,
        detalhes_preparo: Optional[str] = None,
        consulta_id: Optional[int] = None
    ) -> SolicitacaoExame:
        """
        História 1.1: Criar solicitação de exame
        Médico solicita exames para um paciente
        """
        nova_solicitacao = SolicitacaoExame(
            consultaId=consulta_id,
            pacienteId=paciente_id,
            medicoSolicitante=medico_id,
            nomeExame=nome_exame,
            hipoteseDiagnostica=hipotese_diagnostica,
            detalhesPreparo=detalhes_preparo,
            status=StatusSolicitacao.AGUARDANDO_RESULTADO
        )
        
        db.add(nova_solicitacao)
        db.commit()
        db.refresh(nova_solicitacao)
        
        # Registra no prontuário
        log = LogProntuario(
            pacienteId=paciente_id,
            tipoEvento=TipoEvento.SOLICITACAO_EXAME,
            descricao=f"Solicitação de exame: {nome_exame}",
            referenciaId=nova_solicitacao.id
        )
        db.add(log)
        db.commit()
        
        return nova_solicitacao
    
    @staticmethod
    def enviar_resultado_exame(
        db: Session,
        codigo_solicitacao: str,
        data_realizacao: datetime,
        nome_laboratorio: str,
        arquivo_url: str,
        nome_arquivo: str,
        observacoes: Optional[str] = None
    ) -> ResultadoExame:
        """
        História 1.2: Funcionário envia resultado de exame
        Funcionário da clínica faz upload do resultado do exame
        """
        # Busca solicitação pelo código
        solicitacao = db.query(SolicitacaoExame).filter(
            SolicitacaoExame.codigoSolicitacao == codigo_solicitacao
        ).first()
        
        if not solicitacao:
            raise ValueError("Solicitação de exame não encontrada")
        
        # Cria resultado
        novo_resultado = ResultadoExame(
            solicitacaoId=solicitacao.id,
            dataRealizacao=data_realizacao,
            nomeLaboratorio=nome_laboratorio,
            arquivoUrl=arquivo_url,
            nomeArquivo=nome_arquivo,
            observacoes=observacoes
        )
        
        db.add(novo_resultado)
        
        # Atualiza status da solicitação
        solicitacao.status = StatusSolicitacao.RESULTADO_ENVIADO
        
        db.commit()
        db.refresh(novo_resultado)
        
        # Registra no prontuário
        log = LogProntuario(
            pacienteId=solicitacao.pacienteId,
            tipoEvento=TipoEvento.EXAME,
            descricao=f"Resultado de exame enviado: {solicitacao.nomeExame}",
            referenciaId=novo_resultado.id
        )
        db.add(log)
        db.commit()
        
        return novo_resultado
    
    @staticmethod
    def listar_solicitacoes_paciente(
        db: Session, 
        paciente_id: int,
        status: Optional[StatusSolicitacao] = None
    ) -> List[SolicitacaoExame]:
        """
        História 1.2: Lista solicitações de exame do paciente
        Paciente visualiza exames solicitados
        """
        query = db.query(SolicitacaoExame).filter(
            SolicitacaoExame.pacienteId == paciente_id
        )
        
        if status:
            query = query.filter(SolicitacaoExame.status == status)
        
        return query.order_by(SolicitacaoExame.dataSolicitacao.desc()).all()
    
    @staticmethod
    def listar_solicitacoes_medico(
        db: Session, 
        medico_id: int,
        status: Optional[StatusSolicitacao] = None
    ) -> List[SolicitacaoExame]:
        """Lista solicitações criadas por um médico"""
        query = db.query(SolicitacaoExame).filter(
            SolicitacaoExame.medicoSolicitante == medico_id
        )
        
        if status:
            query = query.filter(SolicitacaoExame.status == status)
        
        return query.order_by(SolicitacaoExame.dataSolicitacao.desc()).all()
    
    @staticmethod
    def buscar_solicitacao_por_id(db: Session, solicitacao_id: int) -> Optional[SolicitacaoExame]:
        """Busca solicitação por ID"""
        return db.query(SolicitacaoExame).filter(
            SolicitacaoExame.id == solicitacao_id
        ).first()
    
    @staticmethod
    def buscar_solicitacao_por_codigo(db: Session, codigo: str) -> Optional[SolicitacaoExame]:
        """Busca solicitação por código"""
        return db.query(SolicitacaoExame).filter(
            SolicitacaoExame.codigoSolicitacao == codigo
        ).first()
    
    @staticmethod
    def atualizar_status_solicitacao(
        db: Session,
        solicitacao_id: int,
        novo_status: StatusSolicitacao
    ) -> SolicitacaoExame:
        """Atualiza status de uma solicitação"""
        solicitacao = db.query(SolicitacaoExame).filter(
            SolicitacaoExame.id == solicitacao_id
        ).first()
        
        if not solicitacao:
            raise ValueError("Solicitação não encontrada")
        
        solicitacao.status = novo_status
        db.commit()
        db.refresh(solicitacao)
        
        return solicitacao
    
    @staticmethod
    def buscar_resultados_solicitacao(db: Session, solicitacao_id: int) -> List[ResultadoExame]:
        """Busca resultados de uma solicitação"""
        return db.query(ResultadoExame).filter(
            ResultadoExame.solicitacaoId == solicitacao_id
        ).all()
