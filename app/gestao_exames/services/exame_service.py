"""
Service para Gestão de Exames
Épico 3: Gestão de Exames e Documentação Clínica
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.gestao_exames.models.solicitacao_exame import SolicitacaoExame, StatusSolicitacao
from app.gestao_exames.models.resultado_exame import ResultadoExame
from app.gestao_consultas.models.log_prontuario import LogProntuario, TipoEvento


class ExameService:
    """Service para gerenciar solicitações e resultados de exames"""
    
    @staticmethod
    def criar_solicitacao_exame(
        db: Session,
        consulta_id: int,
        paciente_id: int,
        medico_id: int,
        tipo_exame: str,
        descricao: Optional[str] = None
    ) -> SolicitacaoExame:
        """
        História 1.1: Criar solicitação de exame
        Médico solicita exames a partir de uma consulta
        """
        nova_solicitacao = SolicitacaoExame(
            consultaId=consulta_id,
            pacienteId=paciente_id,
            medicoSolicitante=medico_id,
            tipoExame=tipo_exame,
            descricao=descricao,
            status=StatusSolicitacao.PENDENTE
        )
        
        db.add(nova_solicitacao)
        db.commit()
        db.refresh(nova_solicitacao)
        
        # Registra no prontuário
        log = LogProntuario(
            pacienteId=paciente_id,
            tipoEvento=TipoEvento.SOLICITACAO_EXAME,
            descricao=f"Solicitação de exame: {tipo_exame}",
            referenciaId=nova_solicitacao.id
        )
        db.add(log)
        db.commit()
        
        return nova_solicitacao
    
    @staticmethod
    def enviar_resultado_exame(
        db: Session,
        solicitacao_id: int,
        arquivo_url: str,
        nome_arquivo: str,
        observacoes: Optional[str] = None
    ) -> ResultadoExame:
        """
        História 1.2: Paciente faz upload de resultado de exame
        Paciente envia arquivo com resultado do exame solicitado
        """
        # Verifica se solicitação existe
        solicitacao = db.query(SolicitacaoExame).filter(
            SolicitacaoExame.id == solicitacao_id
        ).first()
        
        if not solicitacao:
            raise ValueError("Solicitação de exame não encontrada")
        
        # Cria resultado
        novo_resultado = ResultadoExame(
            solicitacaoId=solicitacao_id,
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
            descricao=f"Resultado de exame enviado: {solicitacao.tipoExame}",
            referenciaId=novo_resultado.id
        )
        db.add(log)
        db.commit()
        
        return novo_resultado
    
    @staticmethod
    def listar_solicitacoes_paciente(db: Session, paciente_id: int) -> List[SolicitacaoExame]:
        """
        História 1.2: Lista solicitações de exame do paciente
        Paciente visualiza exames solicitados
        """
        return db.query(SolicitacaoExame).filter(
            SolicitacaoExame.pacienteId == paciente_id
        ).order_by(SolicitacaoExame.dataSolicitacao.desc()).all()
    
    @staticmethod
    def listar_solicitacoes_medico(db: Session, medico_id: int) -> List[SolicitacaoExame]:
        """Lista solicitações criadas por um médico"""
        return db.query(SolicitacaoExame).filter(
            SolicitacaoExame.medicoSolicitante == medico_id
        ).order_by(SolicitacaoExame.dataSolicitacao.desc()).all()
    
    @staticmethod
    def buscar_solicitacao_por_id(db: Session, solicitacao_id: int) -> Optional[SolicitacaoExame]:
        """Busca solicitação por ID"""
        return db.query(SolicitacaoExame).filter(
            SolicitacaoExame.id == solicitacao_id
        ).first()
    
    @staticmethod
    def buscar_resultados_solicitacao(db: Session, solicitacao_id: int) -> List[ResultadoExame]:
        """Busca resultados de uma solicitação"""
        return db.query(ResultadoExame).filter(
            ResultadoExame.solicitacaoId == solicitacao_id
        ).all()
