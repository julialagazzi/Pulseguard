from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal

class EmpresaCreate(BaseModel):
    nome: str
    cnpj: str
    setor: str
    limiar_alerta_desvios: Optional[Decimal] = 2.0

class EmpresaUpdate(BaseModel):
    nome: Optional[str] = None
    setor: Optional[str] = None
    limiar_alerta_desvios: Optional[Decimal] = None

class EmpresaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    empresa_id: int
    nome: str
    cnpj: str
    setor: str
    limiar_alerta_desvios: Optional[Decimal] = None
    ativa: bool
