from enum import Enum
from typing import Any, Dict, Optional

import pydantic
from app.analises_diagnosticos.schemas.analises_schemas import (
    ImageAnalysisRequest,
    ImageAnalysisResponse,
)
from app.rabbit.broker import rabbit_router
from faststream.rabbit import RabbitMessage
import logging

logger = logging.getLogger(__name__)

EMAIL_QUEUE = "envio_email_queue"


class TipoEmailEnum(str, Enum):
    """Tipos de email suportados pelo sistema."""

    CADASTRO_USUARIO = "cadastro_usuario"
    CADASTRO_PACIENTE = "cadastro_paciente"
    CONFIRMACAO_CONSULTA = "confirmacao_consulta"
    NOTIFICACAO_SOLICITACAO_EXAME = "notificacao_solicitacao_exame"
    RESULTADO_EXAME_DISPONIVEL = "resultado_exame_disponivel"
    NOTIFICACAO_EXAME_DISPONIVEL = "notificacao_exame_disponivel"
    LAUDO_DISPONIVEL = "laudo_disponivel"
    LEMBRETE_CONSULTA = "lembrete_consulta"
    CONSULTA_CANCELADA = "consulta_cancelada"


class EmailRequest(pydantic.BaseModel):
    """
    Define a estrutura de uma solicitação de envio de email.
    Este objeto será a mensagem enviada para a fila.
    """

    tipo: TipoEmailEnum
    destinatario: str
    nome_destinatario: str
    dados_personalizados: Dict[str, Any] = {}
    assunto_personalizado: Optional[str] = None


async def enviar_email_cadastro_paciente(nome, email, senha_temporaria):
    print("Enviando email de cadastro de paciente...")

    mensagem = EmailRequest(
        tipo=TipoEmailEnum.CADASTRO_PACIENTE,
        destinatario=email,
        nome_destinatario=nome,
        dados_personalizados={
            "nome": nome,
            "email": email,
            "senha_temporaria": senha_temporaria,
        },
        assunto_personalizado="Bem-vindo ao Sistema de Telemedicina!",
    )

    await rabbit_router.broker.publish(mensagem, EMAIL_QUEUE)

    print("Email de cadastro de paciente enviado para a fila.")


async def enviar_email_solicitacao_exame(
    nome_paciente: str,
    email_paciente: str,
    nome_exame: str,
    nome_medico: str,
    codigo_solicitacao: str,
    detalhes_preparo: Optional[str] = None,
):
    """Envia email de notificação de solicitação de exame"""
    print("Enviando email de notificação de solicitação de exame...")

    mensagem = EmailRequest(
        tipo=TipoEmailEnum.NOTIFICACAO_SOLICITACAO_EXAME,
        destinatario=email_paciente,
        nome_destinatario=nome_paciente,
        dados_personalizados={
            "nome_paciente": nome_paciente,
            "nome_exame": nome_exame,
            "nome_medico": nome_medico,
            "codigo_solicitacao": codigo_solicitacao,
            "detalhes_preparo": detalhes_preparo,
        },
        assunto_personalizado="Notificação de Solicitação de Exame",
    )

    await rabbit_router.broker.publish(mensagem, EMAIL_QUEUE)

    print("Email de notificação de solicitação de exame enviado para a fila.")


async def enviar_resultado_exame(
    nome_paciente: str,
    email_paciente: str,
    nome_exame: str,
    codigo_solicitacao: str,
):
    """Envia email de notificação de resultado de exame disponível"""
    print("Enviando email de notificação de resultado de exame...")

    mensagem = EmailRequest(
        tipo=TipoEmailEnum.RESULTADO_EXAME_DISPONIVEL,
        destinatario=email_paciente,
        nome_destinatario=nome_paciente,
        dados_personalizados={
            "nome_paciente": nome_paciente,
            "nome_exame": nome_exame,
            "codigo_solicitacao": codigo_solicitacao,
        },
        assunto_personalizado="Seu Resultado de Exame Está Disponível",
    )

    await rabbit_router.broker.publish(mensagem, EMAIL_QUEUE)

    print("Email de notificação de resultado de exame enviado para a fila.")


async def enviar_notificacao_exame_disponivel(
    data_realizacao: str,
    nome_medico: str,
    nome_paciente: str,
    email_medico: str,
    nome_exame: str,
    codigo_solicitacao: str,
):
    """Envia email de notificação de exame disponível"""
    print("Enviando email de notificação de exame disponível...")

    mensagem = EmailRequest(
        tipo=TipoEmailEnum.NOTIFICACAO_EXAME_DISPONIVEL,
        destinatario=email_medico,
        nome_destinatario=nome_paciente,
        dados_personalizados={
            "nome_medico": nome_medico,
            "nome_paciente": nome_paciente,
            "nome_exame": nome_exame,
            "data_realizacao": data_realizacao,
            "codigo_solicitacao": codigo_solicitacao,
        },
        assunto_personalizado="Seu Exame Está Disponível",
    )

    await rabbit_router.broker.publish(mensagem, EMAIL_QUEUE)

    print("Email de notificação de exame disponível enviado para a fila.")


async def enviar_laudo_disponivel(
    nome_paciente: str,
    email_paciente: str,
    titulo_laudo: str,
    nome_medico: str,
    crm: str,
    data_emissao: str,
):
    """Envia email de notificação de laudo disponível"""
    print("Enviando email de notificação de laudo disponível...")

    mensagem = EmailRequest(
        tipo=TipoEmailEnum.LAUDO_DISPONIVEL,
        destinatario=email_paciente,
        nome_destinatario=nome_paciente,
        dados_personalizados={
            "nome_paciente": nome_paciente,
            "titulo_laudo": titulo_laudo,
            "nome_medico": nome_medico,
            "crm": crm,
            "data_emissao": data_emissao,
        },
        assunto_personalizado="Seu Laudo de Exame Está Disponível",
    )

    await rabbit_router.broker.publish(mensagem, EMAIL_QUEUE)

    print("Email de notificação de laudo disponível enviado para a fila.")


async def enviar_analise_imagem(request: ImageAnalysisRequest):
    """Envia uma solicitação de análise de imagem para a fila RabbitMQ"""
    print("Enviando solicitação de análise de imagem...")

    response = await rabbit_router.broker.request(
        request, "image_analysis", timeout=300
    )

    response_dict = response.body

    print(response_dict)

    return response_dict  # type: ignore
