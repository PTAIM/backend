"""
Rotas Dummy para Teste de Todos os Services
Aplicação: Sistema de Telemedicina
"""
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, time

from app.core.database import get_db

# Imports dos schemas
from app.gestao_perfis.schemas.perfis_schemas import (
    CadastroUsuarioRequest, LoginRequest, CriarPerfilMedicoRequest,
    AtualizarPerfilMedicoRequest, CriarEspecialidadeRequest,
    CriarPerfilPacienteRequest, CriarSumarioSaudeRequest,
    AtualizarSumarioSaudeRequest, AdicionarEspecialidadeRequest
)
from app.gestao_consultas.schemas.consultas_schemas import (
    DefinirHorarioAtendimentoRequest, AgendarConsultaRequest,
    FinalizarConsultaRequest, DiaSemanaEnum, TipoEventoEnum
)
from app.gestao_exames.schemas.exames_schemas import (
    CriarSolicitacaoExameRequest, EnviarResultadoExameRequest,
    CriarLaudoRequest, AtualizarLaudoRequest
)

# Imports dos services
from app.gestao_perfis.services.auth_service import AuthService
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

app = FastAPI(title="Sistema de Telemedicina - API Dummy", version="1.0.0")


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


@app.post("/auth/login", tags=["Autenticação"])
def fazer_login(request: LoginRequest, db: Session = Depends(get_db)):
    """História 1.1: Login de usuário"""
    usuario = AuthService.fazer_login(db, request.email, request.senha)
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return {"message": "Login bem-sucedido", "usuario": {"id": usuario.id, "nome": usuario.nome, "tipo": usuario.tipo}}


# Feature 2: Perfil do Médico
@app.post("/medicos/perfil", tags=["Médicos"])
def criar_perfil_medico(
    request: CriarPerfilMedicoRequest,
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
@app.post("/exames/solicitacoes", tags=["Exames"])
def criar_solicitacao_exame(
    request: CriarSolicitacaoExameRequest,
    db: Session = Depends(get_db)
):
    """História 1.1: Criar solicitação de exame"""
    try:
        solicitacao = ExameService.criar_solicitacao_exame(
            db, request.consulta_id, request.paciente_id, 
            request.medico_id, request.tipo_exame, request.descricao
        )
        return {"message": "Solicitação criada", "solicitacao_id": solicitacao.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/exames/resultados", tags=["Exames"])
def enviar_resultado_exame(
    request: EnviarResultadoExameRequest,
    db: Session = Depends(get_db)
):
    """História 1.2: Paciente envia resultado de exame"""
    try:
        resultado = ExameService.enviar_resultado_exame(
            db, request.solicitacao_id, request.arquivo_url, 
            request.nome_arquivo, request.observacoes
        )
        return {"message": "Resultado enviado", "resultado_id": resultado.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/exames/paciente/{paciente_id}", tags=["Exames"])
def listar_solicitacoes_paciente(paciente_id: int, db: Session = Depends(get_db)):
    """História 1.2: Listar exames do paciente"""
    solicitacoes = ExameService.listar_solicitacoes_paciente(db, paciente_id)
    return {"solicitacoes": [{"id": s.id, "tipo": s.tipoExame, "status": s.status.value} for s in solicitacoes]}


# Feature 2: Visualização de Prontuário
@app.get("/prontuario/{paciente_id}", tags=["Prontuário"])
def visualizar_prontuario(
    paciente_id: int,
    tipo_evento: Optional[TipoEventoEnum] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    db: Session = Depends(get_db)
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

# Feature 1: Fila de Trabalho
@app.get("/laudos/fila/{medico_id}", tags=["Laudos"])
def obter_fila_trabalho(medico_id: int, db: Session = Depends(get_db)):
    """História 1.1: Fila de trabalho / Caixa de entrada"""
    resultados = LaudoService.obter_fila_trabalho(db, medico_id)
    return {
        "resultados_pendentes": [
            {
                "id": r.id,
                "arquivo": r.arquivoUrl,
                "data_upload": r.dataUpload.isoformat()
            } for r in resultados
        ]
    }


# Feature 2: Emissão de Laudo Médico
@app.post("/laudos", tags=["Laudos"])
def criar_laudo(
    request: CriarLaudoRequest,
    db: Session = Depends(get_db)
):
    """História 2.1: Emitir laudo médico"""
    try:
        laudo = LaudoService.criar_laudo(
            db, request.resultado_exame_id, request.medico_id, 
            request.achados, request.impressao_diagnostica, request.recomendacoes
        )
        return {"message": "Laudo criado", "laudo_id": laudo.id, "status": laudo.status.value}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/laudos/{laudo_id}", tags=["Laudos"])
def atualizar_laudo(
    laudo_id: int,
    request: AtualizarLaudoRequest,
    db: Session = Depends(get_db)
):
    """História 2.1: Atualizar laudo em rascunho"""
    try:
        laudo = LaudoService.atualizar_laudo(
            db, laudo_id, request.achados, 
            request.impressao_diagnostica, request.recomendacoes
        )
        return {"message": "Laudo atualizado"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/laudos/{laudo_id}/finalizar", tags=["Laudos"])
def finalizar_laudo(laudo_id: int, db: Session = Depends(get_db)):
    """História 2.1: Finalizar laudo"""
    try:
        laudo = LaudoService.finalizar_laudo(db, laudo_id)
        return {"message": "Laudo finalizado e registrado no prontuário"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/laudos/medico/{medico_id}", tags=["Laudos"])
def listar_laudos_medico(medico_id: int, db: Session = Depends(get_db)):
    """Listar laudos emitidos pelo médico"""
    laudos = LaudoService.listar_laudos_medico(db, medico_id)
    return {"laudos": [{"id": l.id, "status": l.status.value, "data_emissao": l.dataEmissao.isoformat()} for l in laudos]}


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
