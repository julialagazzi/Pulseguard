from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    papel: str

class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    usuario_id: int
    nome: str
    email: str
    papel: str
    ativo: bool
    criado_em: Optional[datetime] = None
