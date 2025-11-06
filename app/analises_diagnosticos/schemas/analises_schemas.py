from typing import List

from pydantic import BaseModel, Field


class AnalisarImagemRequest(BaseModel):
    nome_arquivo: str = Field(..., description="Localização da imagem a ser analisada")


class ImageAnalysisResponse(BaseModel):
    analysis_text: str


class ImageAnalysisRequest(BaseModel):
    image_bytes: bytes
    mime_type: str
