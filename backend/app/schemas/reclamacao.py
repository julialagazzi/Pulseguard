from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

class ReclamacaoCreate(BaseModel):
    empresa_id: int
    data_reclamacao: date
    categoria: str
    texto: str
    status: str = "aberta"

class ReclamacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reclamacao_id: int
    empresa_id: int
    data_reclamacao: date
    categoria: str
    texto: str
    status: str
    checksum_sha256: str
