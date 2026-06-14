from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class AlertaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    alerta_id: int
    empresa_id: int
    data_deteccao: Optional[datetime] = None
    severidade: str
    volume_dia: int
    media_historica: Decimal
    variacao_pct: Decimal
    categoria_dominante: str
    status_alerta: str
