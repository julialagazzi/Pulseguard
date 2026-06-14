from pydantic import BaseModel
from typing import List, Optional

class KPIs(BaseModel):
    total_reclamacoes: int
    variacao_pct: float
    alertas_ativos: int
    empresas_monitoradas: int

class EvolucaoItem(BaseModel):
    data: str
    volume: int

class RankingItem(BaseModel):
    empresa: str
    total: int
    variacao: float
    status: str

class CategoriaItem(BaseModel):
    categoria: str
    count: int
    pct: float
