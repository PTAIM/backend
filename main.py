"""
Rotas Dummy para Teste de Todos os Services
Aplicação: Sistema de Telemedicina
"""
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, time

from app.core.database import get_db
from app.core.auth_dependencies import (
    get_current_user, get_current_active_user, require_medico, 
    require_paciente, require_admin
)

# Imports dos schemas
from app.gestao_perfis.schemas.perfis_schemas import (
    CadastroUsuarioRequest, LoginRequest, LoginResponse, UsuarioResponse,
    CriarPerfilMedicoRequest, AtualizarPerfilMedicoRequest, CriarEspecialidadeRequest,
    CriarPerfilPacienteRequest, CriarSumarioSaudeRequest,
    AtualizarSumarioSaudeRequest, AdicionarEspecialidadeRequest
)
from app.gestao_consultas.schemas.consultas_schemas import (
    DefinirHorarioAtendimentoRequest, AgendarConsultaRequest,
    FinalizarConsultaRequest, DiaSemanaEnum, TipoEventoEnum
)
from app.gestao_exames.schemas.exames_schemas import (
    CriarSolicitacaoExameRequest, EnviarResultadoExameRequest,
    CriarLaudoRequest, AtualizarLaudoRequest, AtualizarStatusSolicitacaoRequest
)

# Imports dos services
# Importar services
from app.gestao_perfis.services.auth_service import AuthService
from app.gestao_perfis.models.usuario import Usuario
from app.gestao_perfis.services.medico_service import MedicoService, EspecialidadeService
from app.gestao_perfis.services.paciente_service import PacienteService, SumarioSaudeService
from app.gestao_consultas.services.agenda_service import AgendaService
from app.gestao_consultas.services.consulta_service import ConsultaService
from app.gestao_consultas.services.prontuario_service import ProntuarioService
from app.gestao_exames.services.exame_service import ExameService
from app.gestao_exames.services.laudo_service import LaudoService

# Imports dos modelos/enums
from app.gestao_perfis.models.usuario import TipoUsuario
from app.gestao_perfis.models.agenda import DiaSemana
from app.gestao_consultas.models.log_prontuario import TipoEvento

app = FastAPI(
    title="Sistema de Telemedicina", 
    version="1.0.0",
    description="API para sistema de telemedicina com autenticação JWT"
)

# Configurar segurança JWT no Swagger
security = HTTPBearer()


# ==========================================
# ÉPICO 1: GESTÃO DE PERFIS
# ==========================================

# Feature 1: Autenticação e Cadastro
@app.post("/auth/cadastro", tags=["Autenticação"])
def cadastrar_usuario(
    request: CadastroUsuarioRequest,
    db: Session = Depends(get_db)
):
    """História 1.1: Cadastro de usuário"""
    try:
        tipo_enum = TipoUsuario(request.tipo.value)
        usuario = AuthService.cadastrar_usuario(
            db, request.nome, request.email, request.senha, 
            request.cpf, tipo_enum, request.telefone
        )
        return {"message": "Usuário cadastrado com sucesso", "usuario_id": usuario.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", tags=["Autenticação"], response_model=LoginResponse)
def fazer_login(request: LoginRequest, db: Session = Depends(get_db)):
    """História 1.1: Login de usuário com token JWT"""
    usuario = AuthService.fazer_login(db, request.email, request.senha)
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    # Cria token JWT
    access_token = AuthService.criar_token_acesso(usuario)
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        usuario=UsuarioResponse(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            tipo=usuario.tipo.value
        )
    )


@app.get("/auth/me", tags=["Autenticação"], response_model=UsuarioResponse)
def get_current_user_info(current_user: Usuario = Depends(get_current_user)):
    """Obter informações do usuário logado"""
    return UsuarioResponse(
        id=current_user.id,
        nome=current_user.nome,
        email=current_user.email,
        tipo=current_user.tipo.value
    )


# Feature 2: Perfil do Médico
@app.post("/medicos/perfil", tags=["Médicos"])
def criar_perfil_medico(
    request: CriarPerfilMedicoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)  # Só admin pode criar perfis médicos
):
    """História 2.1: Criar perfil do médico"""
    try:
        medico = MedicoService.criar_perfil_medico(
            db, request.usuario_id, request.crm, request.biografia, 
            request.duracao_consulta, request.link_sala_virtual
        )
        return {"message": "Perfil médico criado", "medico_id": medico.usuarioId}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/medicos/perfil/{usuario_id}", tags=["Médicos"])
def atualizar_perfil_medico(
    usuario_id: int,
    request: AtualizarPerfilMedicoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_medico)  # Só médicos podem atualizar perfis
):
    """História 2.1: Atualizar perfil do médico"""
    try:
        medico = MedicoService.atualizar_perfil_medico(
            db, usuario_id, request.biografia, 
            request.duracao_consulta, request.link_sala_virtual
        )
        return {"message": "Perfil atualizado", "medico": {"biografia": medico.biografia}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/medicos/{medico_id}/especialidades", tags=["Médicos"])
def adicionar_especialidade(
    medico_id: int, 
    request: AdicionarEspecialidadeRequest, 
    db: Session = Depends(get_db)
):
    """História 2.1: Adicionar especialidade ao médico"""
    try:
        MedicoService.adicionar_especialidade(db, medico_id, request.especialidade_id)
        return {"message": "Especialidade adicionada"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/medicos/especialidade/{especialidade_id}", tags=["Médicos"])
def buscar_medicos_por_especialidade(especialidade_id: int, db: Session = Depends(get_db)):
    """História 2.1: Buscar médicos por especialidade"""
    medicos = MedicoService.buscar_medicos_por_especialidade(db, especialidade_id)
    return {"medicos": [{"id": m.usuarioId, "crm": m.crm} for m in medicos]}


@app.post("/especialidades", tags=["Especialidades"])
def criar_especialidade(request: CriarEspecialidadeRequest, db: Session = Depends(get_db)):
    """Criar nova especialidade"""
    try:
        especialidade = EspecialidadeService.criar_especialidade(db, request.nome)
        return {"message": "Especialidade criada", "id": especialidade.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/especialidades", tags=["Especialidades"])
def listar_especialidades(db: Session = Depends(get_db)):
    """Listar todas especialidades"""
    especialidades = EspecialidadeService.listar_especialidades(db)
    return {"especialidades": [{"id": e.id, "nome": e.nome} for e in especialidades]}


# Feature 3: Sumário de Saúde do Paciente
@app.post("/pacientes/perfil", tags=["Pacientes"])
def criar_perfil_paciente(
    request: CriarPerfilPacienteRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)  # Usuário deve estar logado
):
    """Criar perfil do paciente"""
    try:
        paciente = PacienteService.criar_perfil_paciente(
            db, request.usuario_id, request.data_nascimento, request.endereco
        )
        return {"message": "Perfil paciente criado", "paciente_id": paciente.usuarioId}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/pacientes/{paciente_id}/sumario", tags=["Pacientes"])
def criar_sumario_saude(
    paciente_id: int,
    request: CriarSumarioSaudeRequest,
    db: Session = Depends(get_db)
):
    """História 3.1: Registrar sumário de saúde"""
    try:
        sumario = SumarioSaudeService.criar_sumario_saude(
            db, paciente_id, request.historico_doencas, 
            request.alergias, request.medicacoes
        )
        return {"message": "Sumário criado", "sumario_id": sumario.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/sumarios/{sumario_id}", tags=["Pacientes"])
def atualizar_sumario_saude(
    sumario_id: int,
    request: AtualizarSumarioSaudeRequest,
    db: Session = Depends(get_db)
):
    """História 3.1: Atualizar sumário de saúde"""
    try:
        sumario = SumarioSaudeService.atualizar_sumario_saude(
            db, sumario_id, request.historico_doencas, 
            request.alergias, request.medicacoes
        )
        return {"message": "Sumário atualizado"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/pacientes/{paciente_id}/sumario", tags=["Pacientes"])
def buscar_sumario_paciente(paciente_id: int, db: Session = Depends(get_db)):
    """História 3.1: Buscar sumário de saúde do paciente"""
    sumario = SumarioSaudeService.buscar_sumario_por_paciente(db, paciente_id)
    if not sumario:
        raise HTTPException(status_code=404, detail="Sumário não encontrado")
    return {
        "sumario": {
            "id": sumario.id,
            "historico_doencas": sumario.historicoDoencas,
            "alergias": sumario.alergias,
            "medicacoes": sumario.medicacoes
        }
    }


# ==========================================
# ÉPICO 2: CICLO DE VIDA DE CONSULTAS
# ==========================================

# Feature 1: Gestão de Agenda
@app.post("/agendas", tags=["Agendas"])
def definir_horario_atendimento(
    request: DefinirHorarioAtendimentoRequest,
    db: Session = Depends(get_db)
):
    """História 1.1: Definir horários de atendimento"""
    try:
        from app.gestao_perfis.models.agenda import DiaSemana
        from datetime import time
        
        dia_enum = DiaSemana(request.dia_semana.value)
        hora_parts = request.hora.split(":")
        hora_time = time(int(hora_parts[0]), int(hora_parts[1]))
        
        agenda = AgendaService.definir_horario_atendimento(db, request.medico_id, dia_enum, hora_time)
        return {"message": "Horário definido", "agenda_id": agenda.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/agendas/medico/{medico_id}", tags=["Agendas"])
def listar_horarios_medico(
    medico_id: int, 
    dia_semana: Optional[DiaSemanaEnum] = None, 
    db: Session = Depends(get_db)
):
    """História 1.1: Listar horários do médico"""
    from app.gestao_perfis.models.agenda import DiaSemana
    
    dia_enum = DiaSemana(dia_semana.value) if dia_semana else None
    horarios = AgendaService.listar_horarios_medico(db, medico_id, dia_enum)
    return {"horarios": [{"id": h.id, "dia": h.diaSemana.value, "hora": str(h.hora)} for h in horarios]}


@app.get("/agendas/medico/{medico_id}/disponiveis", tags=["Agendas"])
def obter_horarios_disponiveis(
    medico_id: int,
    data_inicio: str,  # Formato "YYYY-MM-DD"
    data_fim: str,
    db: Session = Depends(get_db)
):
    """História 1.1 e 1.2: Mostrar horários disponíveis"""
    try:
        dt_inicio = datetime.fromisoformat(data_inicio)
        dt_fim = datetime.fromisoformat(data_fim)
        horarios = AgendaService.obter_horarios_disponiveis(db, medico_id, dt_inicio, dt_fim)
        return {"horarios_disponiveis": [h.isoformat() for h in horarios]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Feature 1: Gestão de Consultas
@app.post("/consultas", tags=["Consultas"])
def agendar_consulta(
    request: AgendarConsultaRequest,
    db: Session = Depends(get_db)
):
    """História 1.2: Agendar consulta"""
    try:
        dt = datetime.fromisoformat(request.data_hora.replace(" ", "T"))
        consulta = ConsultaService.agendar_consulta(
            db, request.paciente_id, request.medico_id, 
            dt, request.motivo_consulta
        )
        return {"message": "Consulta agendada", "consulta_id": consulta.id, "link_sala": consulta.linkSalaVirtual}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/consultas/paciente/{paciente_id}", tags=["Consultas"])
def listar_consultas_paciente(paciente_id: int, apenas_futuras: bool = False, db: Session = Depends(get_db)):
    """História 1.3: Visualizar consultas do paciente"""
    consultas = ConsultaService.listar_consultas_paciente(db, paciente_id, apenas_futuras)
    return {"consultas": [{"id": c.id, "data_hora": c.dataHora.isoformat(), "status": c.status.value} for c in consultas]}


@app.get("/consultas/medico/{medico_id}", tags=["Consultas"])
def listar_consultas_medico(medico_id: int, apenas_futuras: bool = False, db: Session = Depends(get_db)):
    """História 1.3: Visualizar consultas do médico"""
    consultas = ConsultaService.listar_consultas_medico(db, medico_id, apenas_futuras)
    return {"consultas": [{"id": c.id, "data_hora": c.dataHora.isoformat(), "status": c.status.value} for c in consultas]}


# Feature 2: Realização da Teleconsulta
@app.post("/consultas/{consulta_id}/iniciar", tags=["Consultas"])
def iniciar_consulta(consulta_id: int, db: Session = Depends(get_db)):
    """História 2.1: Iniciar teleconsulta"""
    try:
        consulta = ConsultaService.iniciar_consulta(db, consulta_id)
        return {"message": "Consulta iniciada", "link_sala": consulta.linkSalaVirtual}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/consultas/{consulta_id}/finalizar", tags=["Consultas"])
def finalizar_consulta(
    consulta_id: int, 
    request: Optional[FinalizarConsultaRequest] = None, 
    db: Session = Depends(get_db)
):
    """Finalizar consulta"""
    try:
        observacoes = request.observacoes if request else None
        consulta = ConsultaService.finalizar_consulta(db, consulta_id, observacoes)
        return {"message": "Consulta finalizada"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================
# ÉPICO 3: GESTÃO DE EXAMES E DOCUMENTAÇÃO
# ==========================================

# Feature 1: Gestão de Exames
@app.post("/solicitacoes", tags=["Exames"])
def criar_solicitacao_exame(
    request: CriarSolicitacaoExameRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_medico)
):
    """História 1.1: Criar solicitação de exame"""
    try:
        solicitacao = ExameService.criar_solicitacao_exame(
            db, request.paciente_id, current_user.id,
            request.nome_exame, request.hipotese_diagnostica, request.detalhes_preparo
        )
        return {
            "id": solicitacao.id,
            "codigo_solicitacao": solicitacao.codigoSolicitacao,
            "status": solicitacao.status.value
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/solicitacoes", tags=["Exames"])
def listar_solicitacoes(
    status: Optional[str] = None,
    paciente_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_medico)
):
    """Listar solicitações com filtros"""
    try:
        from app.gestao_exames.models.solicitacao_exame import StatusSolicitacao
        
        status_enum = StatusSolicitacao(status) if status else None
        
        if paciente_id:
            solicitacoes = ExameService.listar_solicitacoes_paciente(db, paciente_id, status_enum)
        else:
            solicitacoes = ExameService.listar_solicitacoes_medico(db, current_user.id, status_enum)
        
        return {
            "solicitacoes": [
                {
                    "id": s.id,
                    "codigo_solicitacao": s.codigoSolicitacao,
                    "paciente_id": s.pacienteId,
                    "paciente_nome": s.paciente.usuario.nome if s.paciente else None,
                    "paciente_cpf": s.paciente.usuario.cpf if s.paciente else None,
                    "medico_id": s.medicoSolicitante,
                    "medico_nome": s.medico.usuario.nome if s.medico else None,
                    "medico_crm": s.medico.crm if s.medico else None,
                    "nome_exame": s.nomeExame,
                    "hipotese_diagnostica": s.hipoteseDiagnostica,
                    "detalhes_preparo": s.detalhesPreparo,
                    "status": s.status.value,
                    "data_solicitacao": s.dataSolicitacao.isoformat()
                } for s in solicitacoes
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/solicitacoes/{solicitacao_id}", tags=["Exames"])
def obter_solicitacao(
    solicitacao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter detalhes de uma solicitação"""
    solicitacao = ExameService.buscar_solicitacao_por_id(db, solicitacao_id)
    
    if not solicitacao:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    
    return {
        "id": solicitacao.id,
        "codigo_solicitacao": solicitacao.codigoSolicitacao,
        "paciente_id": solicitacao.pacienteId,
        "paciente_nome": solicitacao.paciente.usuario.nome if solicitacao.paciente else None,
        "paciente_cpf": solicitacao.paciente.usuario.cpf if solicitacao.paciente else None,
        "medico_id": solicitacao.medicoSolicitante,
        "medico_nome": solicitacao.medico.usuario.nome if solicitacao.medico else None,
        "medico_crm": solicitacao.medico.crm if solicitacao.medico else None,
        "nome_exame": solicitacao.nomeExame,
        "hipotese_diagnostica": solicitacao.hipoteseDiagnostica,
        "detalhes_preparo": solicitacao.detalhesPreparo,
        "status": solicitacao.status.value,
        "data_solicitacao": solicitacao.dataSolicitacao.isoformat()
    }


@app.put("/solicitacoes/{solicitacao_id}", tags=["Exames"])
def atualizar_status_solicitacao(
    solicitacao_id: int,
    request: AtualizarStatusSolicitacaoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_medico)
):
    """Atualizar status da solicitação (ex: cancelar)"""
    try:
        from app.gestao_exames.models.solicitacao_exame import StatusSolicitacao
        
        solicitacao = ExameService.atualizar_status_solicitacao(
            db, solicitacao_id, StatusSolicitacao(request.status.value)
        )
        return {
            "id": solicitacao.id,
            "status": solicitacao.status.value
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/resultados", tags=["Exames"])
def enviar_resultado_exame(
    request: EnviarResultadoExameRequest,
    db: Session = Depends(get_db)
):
    """História 1.2: Funcionário envia resultado de exame"""
    try:
        # TODO: Handle file upload here - for now assuming arquivo_url is provided
        arquivo_url = "/uploads/temp.pdf"  # Placeholder
        nome_arquivo = "resultado.pdf"  # Placeholder
        
        resultado = ExameService.enviar_resultado_exame(
            db, request.codigo_solicitacao, request.data_realizacao,
            request.nome_laboratorio, arquivo_url, nome_arquivo, request.observacoes
        )
        return {"message": "Resultado enviado", "resultado_id": resultado.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/exames", tags=["Exames"])
def listar_exames(
    paciente_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar exames (resultados) com filtros"""
    try:
        # Se paciente_id não for fornecido e usuário for paciente, usa o próprio ID
        if not paciente_id and current_user.tipo.value == "paciente":
            from app.gestao_perfis.models.paciente import Paciente
            paciente = db.query(Paciente).filter(Paciente.usuarioId == current_user.id).first()
            if paciente:
                paciente_id = paciente.usuarioId
        
        if not paciente_id:
            raise HTTPException(status_code=400, detail="paciente_id é obrigatório")
        
        solicitacoes = ExameService.listar_solicitacoes_paciente(db, paciente_id)
        
        exames = []
        for sol in solicitacoes:
            for resultado in sol.resultados:
                exames.append({
                    "id": resultado.id,
                    "solicitacao_id": sol.id,
                    "codigo_solicitacao": sol.codigoSolicitacao,
                    "nome_exame": sol.nomeExame,
                    "data_realizacao": resultado.dataRealizacao.isoformat(),
                    "nome_laboratorio": resultado.nomeLaboratorio,
                    "nome_arquivo": resultado.nomeArquivo,
                    "url_arquivo": resultado.arquivoUrl
                })
        
        return {"exames": exames}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Feature 2: Visualização de Prontuário
@app.get("/prontuario/{paciente_id}", tags=["Prontuário"])
def visualizar_prontuario(
    paciente_id: int,
    tipo_evento: Optional[TipoEventoEnum] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_medico)  # Só médicos podem ver prontuários
):
    """História 2.1: Visualizar prontuário com filtros"""
    try:
        from app.gestao_consultas.models.log_prontuario import TipoEvento
        
        tipo_enum = TipoEvento(tipo_evento.value) if tipo_evento else None
        dt_inicio = datetime.fromisoformat(data_inicio) if data_inicio else None
        dt_fim = datetime.fromisoformat(data_fim) if data_fim else None
        
        logs = ProntuarioService.visualizar_prontuario(db, paciente_id, tipo_enum, dt_inicio, dt_fim)
        return {
            "eventos": [
                {
                    "id": log.id,
                    "tipo": log.tipoEvento.value,
                    "data": log.dataEvento.isoformat(),
                    "descricao": log.descricao
                } for log in logs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/prontuario/{paciente_id}/completo", tags=["Prontuário"])
def obter_historico_completo(paciente_id: int, db: Session = Depends(get_db)):
    """História 2.1: Histórico completo do paciente"""
    historico = ProntuarioService.obter_historico_completo(db, paciente_id)
    return {
        "total_consultas": len(historico["consultas"]),
        "total_exames": len(historico["exames"]),
        "total_eventos": len(historico["timeline"])
    }


# ==========================================
# ÉPICO 4: ANÁLISE, DIAGNÓSTICO E LAUDOS
# ==========================================

# Feature 2: Emissão de Laudo Médico
@app.post("/laudos", tags=["Laudos"])
def criar_laudo(
    request: CriarLaudoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_medico)
):
    """História 2.1: Emitir laudo médico"""
    try:
        laudo = LaudoService.criar_laudo(
            db, request.paciente_id, current_user.id,
            request.titulo, request.descricao, request.exames_ids
        )
        return {
            "id": laudo.id,
            "status": laudo.status.value
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/laudos", tags=["Laudos"])
def listar_laudos(
    paciente_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar laudos com filtros"""
    try:
        from app.gestao_exames.models.laudo import StatusLaudo
        from app.gestao_exames.models.laudo_resultado import LaudoResultado
        from app.gestao_exames.models.resultado_exame import ResultadoExame
        
        status_enum = StatusLaudo(status) if status else None
        
        # Se for paciente, lista apenas seus próprios laudos
        if current_user.tipo.value == "paciente":
            from app.gestao_perfis.models.paciente import Paciente
            paciente = db.query(Paciente).filter(Paciente.usuarioId == current_user.id).first()
            if paciente:
                paciente_id = paciente.usuarioId
            laudos = LaudoService.listar_laudos_paciente(db, paciente_id, status_enum)
        elif paciente_id:
            # Médico listando laudos de um paciente específico
            laudos = LaudoService.listar_laudos_paciente(db, paciente_id, status_enum)
        else:
            # Médico listando seus próprios laudos
            laudos = LaudoService.listar_laudos_medico(db, current_user.id, status_enum)
        
        resultado_laudos = []
        for laudo in laudos:
            # Busca exames associados
            laudo_resultados = db.query(LaudoResultado).filter(
                LaudoResultado.laudoId == laudo.id
            ).all()
            
            exames = []
            paciente_info = None
            for lr in laudo_resultados:
                resultado = db.query(ResultadoExame).filter(
                    ResultadoExame.id == lr.resultadoExameId
                ).first()
                if resultado and resultado.solicitacao:
                    exames.append({
                        "id": resultado.id,
                        "solicitacao_id": resultado.solicitacaoId,
                        "codigo_solicitacao": resultado.solicitacao.codigoSolicitacao,
                        "nome_exame": resultado.solicitacao.nomeExame,
                        "data_realizacao": resultado.dataRealizacao.isoformat(),
                        "nome_laboratorio": resultado.nomeLaboratorio,
                        "nome_arquivo": resultado.nomeArquivo,
                        "url_arquivo": resultado.arquivoUrl
                    })
                    if not paciente_info and resultado.solicitacao.paciente:
                        paciente_info = {
                            "paciente_id": resultado.solicitacao.pacienteId,
                            "paciente_nome": resultado.solicitacao.paciente.usuario.nome,
                            "paciente_cpf": resultado.solicitacao.paciente.usuario.cpf
                        }
            
            if paciente_info:
                resultado_laudos.append({
                    "id": laudo.id,
                    "paciente_id": paciente_info["paciente_id"],
                    "paciente_nome": paciente_info["paciente_nome"],
                    "paciente_cpf": paciente_info["paciente_cpf"],
                    "medico_id": laudo.medicoId,
                    "medico_nome": laudo.medico.usuario.nome if laudo.medico else None,
                    "medico_crm": laudo.medico.crm if laudo.medico else None,
                    "titulo": laudo.titulo,
                    "descricao": laudo.descricao,
                    "status": laudo.status.value,
                    "data_emissao": laudo.dataEmissao.isoformat(),
                    "exames": exames
                })
        
        return {"laudos": resultado_laudos}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/laudos/{laudo_id}", tags=["Laudos"])
def obter_laudo(
    laudo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter detalhes de um laudo"""
    try:
        from app.gestao_exames.models.laudo_resultado import LaudoResultado
        from app.gestao_exames.models.resultado_exame import ResultadoExame
        
        laudo = LaudoService.buscar_laudo_por_id(db, laudo_id)
        
        if not laudo:
            raise HTTPException(status_code=404, detail="Laudo não encontrado")
        
        # Busca exames associados
        laudo_resultados = db.query(LaudoResultado).filter(
            LaudoResultado.laudoId == laudo.id
        ).all()
        
        exames = []
        paciente_info = None
        for lr in laudo_resultados:
            resultado = db.query(ResultadoExame).filter(
                ResultadoExame.id == lr.resultadoExameId
            ).first()
            if resultado and resultado.solicitacao:
                exames.append({
                    "id": resultado.id,
                    "solicitacao_id": resultado.solicitacaoId,
                    "codigo_solicitacao": resultado.solicitacao.codigoSolicitacao,
                    "nome_exame": resultado.solicitacao.nomeExame,
                    "data_realizacao": resultado.dataRealizacao.isoformat(),
                    "nome_laboratorio": resultado.nomeLaboratorio,
                    "nome_arquivo": resultado.nomeArquivo,
                    "url_arquivo": resultado.arquivoUrl
                })
                if not paciente_info and resultado.solicitacao.paciente:
                    paciente_info = {
                        "paciente_id": resultado.solicitacao.pacienteId,
                        "paciente_nome": resultado.solicitacao.paciente.usuario.nome,
                        "paciente_cpf": resultado.solicitacao.paciente.usuario.cpf
                    }
        
        if not paciente_info:
            raise HTTPException(status_code=404, detail="Informações do paciente não encontradas")
        
        return {
            "id": laudo.id,
            "paciente_id": paciente_info["paciente_id"],
            "paciente_nome": paciente_info["paciente_nome"],
            "paciente_cpf": paciente_info["paciente_cpf"],
            "medico_id": laudo.medicoId,
            "medico_nome": laudo.medico.usuario.nome if laudo.medico else None,
            "medico_crm": laudo.medico.crm if laudo.medico else None,
            "titulo": laudo.titulo,
            "descricao": laudo.descricao,
            "status": laudo.status.value,
            "data_emissao": laudo.dataEmissao.isoformat(),
            "exames": exames
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/laudos/{laudo_id}", tags=["Laudos"])
def atualizar_laudo(
    laudo_id: int,
    request: AtualizarLaudoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_medico)
):
    """História 2.1: Atualizar laudo em rascunho"""
    try:
        laudo = LaudoService.atualizar_laudo(
            db, laudo_id, request.titulo, request.descricao
        )
        return {"message": "Laudo atualizado"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/laudos/{laudo_id}/finalizar", tags=["Laudos"])
def finalizar_laudo(
    laudo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_medico)
):
    """História 2.1: Finalizar laudo"""
    try:
        laudo = LaudoService.finalizar_laudo(db, laudo_id)
        return {"message": "Laudo finalizado e registrado no prontuário"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================
# DASHBOARD
# ==========================================

@app.get("/dashboard/stats", tags=["Dashboard"])
def obter_estatisticas_dashboard(
    periodo: Optional[str] = "30d",
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_medico)
):
    """Estatísticas do dashboard para médicos"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func, extract
        from app.gestao_exames.models.solicitacao_exame import SolicitacaoExame
        from app.gestao_exames.models.resultado_exame import ResultadoExame
        from app.gestao_exames.models.laudo import Laudo
        
        # Calcula data de início baseado no período
        data_fim = datetime.utcnow()
        if periodo == "7d":
            data_inicio = data_fim - timedelta(days=7)
        elif periodo == "90d":
            data_inicio = data_fim - timedelta(days=90)
        elif periodo == "1y":
            data_inicio = data_fim - timedelta(days=365)
        elif periodo == "all":
            data_inicio = datetime(2000, 1, 1)
        else:  # 30d (default)
            data_inicio = data_fim - timedelta(days=30)
        
        # Total de solicitações do médico
        total_solicitacoes = db.query(func.count(SolicitacaoExame.id)).filter(
            SolicitacaoExame.medicoSolicitante == current_user.id,
            SolicitacaoExame.dataSolicitacao >= data_inicio
        ).scalar()
        
        # Exames recebidos (com resultado)
        exames_recebidos = db.query(func.count(ResultadoExame.id)).join(
            SolicitacaoExame, ResultadoExame.solicitacaoId == SolicitacaoExame.id
        ).filter(
            SolicitacaoExame.medicoSolicitante == current_user.id,
            ResultadoExame.dataUpload >= data_inicio
        ).scalar()
        
        # Laudos emitidos
        laudos_emitidos = db.query(func.count(Laudo.id)).filter(
            Laudo.medicoId == current_user.id,
            Laudo.dataEmissao >= data_inicio
        ).scalar()
        
        # Total de pacientes distintos
        total_pacientes = db.query(func.count(func.distinct(SolicitacaoExame.pacienteId))).filter(
            SolicitacaoExame.medicoSolicitante == current_user.id,
            SolicitacaoExame.dataSolicitacao >= data_inicio
        ).scalar()
        
        # Solicitações por mês
        solicitacoes_por_mes = db.query(
            func.to_char(SolicitacaoExame.dataSolicitacao, 'YYYY-MM').label('mes'),
            func.count(SolicitacaoExame.id).label('total')
        ).filter(
            SolicitacaoExame.medicoSolicitante == current_user.id,
            SolicitacaoExame.dataSolicitacao >= data_inicio
        ).group_by('mes').order_by('mes').all()
        
        # Laudos por mês
        laudos_por_mes = db.query(
            func.to_char(Laudo.dataEmissao, 'YYYY-MM').label('mes'),
            func.count(Laudo.id).label('total')
        ).filter(
            Laudo.medicoId == current_user.id,
            Laudo.dataEmissao >= data_inicio
        ).group_by('mes').order_by('mes').all()
        
        return {
            "resumo": {
                "total_solicitacoes": total_solicitacoes or 0,
                "exames_recebidos": exames_recebidos or 0,
                "laudos_emitidos": laudos_emitidos or 0,
                "total_pacientes": total_pacientes or 0
            },
            "solicitacoes_por_mes": [
                {"mes": row.mes, "total": row.total} for row in solicitacoes_por_mes
            ],
            "laudos_por_mes": [
                {"mes": row.mes, "total": row.total} for row in laudos_por_mes
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================
# ROTA DE SAÚDE
# ==========================================

@app.get("/")
def health_check():
    """Health check"""
    return {
        "status": "ok",
        "message": "Sistema de Telemedicina - API funcionando",
        "epicos_implementados": [
            "Épico 1: Gestão de Perfis",
            "Épico 2: Ciclo de Vida de Consultas",
            "Épico 3: Gestão de Exames e Documentação Clínica",
            "Épico 4: Análise, Diagnóstico e Laudos"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
