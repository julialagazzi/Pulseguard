from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from typing import Optional
from ..database import get_db
from ..models.reclamacao import Reclamacao
from ..models.alerta import Alerta
from ..models.empresa import Empresa
from ..schemas.dashboard import KPIs, EvolucaoItem, RankingItem, CategoriaItem
from ..utils.security import get_current_user
from typing import List

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def parse_periodo(periodo: str) -> int:
    return int(periodo.replace("d", ""))

@router.get("/kpis", response_model=KPIs)
def kpis(periodo: str = "30d", db: Session = Depends(get_db), _=Depends(get_current_user)):
    dias = parse_periodo(periodo)
    hoje = date.today()
    inicio = hoje - timedelta(days=dias)
    inicio_ant = inicio - timedelta(days=dias)

    total = db.query(func.count(Reclamacao.reclamacao_id)).filter(
        Reclamacao.data_reclamacao >= inicio
    ).scalar() or 0

    total_ant = db.query(func.count(Reclamacao.reclamacao_id)).filter(
        Reclamacao.data_reclamacao >= inicio_ant,
        Reclamacao.data_reclamacao < inicio
    ).scalar() or 0

    variacao = ((total - total_ant) / total_ant * 100) if total_ant > 0 else 0.0

    alertas_ativos = db.query(func.count(Alerta.alerta_id)).filter(
        Alerta.status_alerta == "ativo"
    ).scalar() or 0

    empresas = db.query(func.count(Empresa.empresa_id)).filter(Empresa.ativa == True).scalar() or 0

    return KPIs(
        total_reclamacoes=total,
        variacao_pct=round(variacao, 2),
        alertas_ativos=alertas_ativos,
        empresas_monitoradas=empresas
    )

@router.get("/evolucao", response_model=List[EvolucaoItem])
def evolucao(periodo: str = "30d", empresa_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    dias = parse_periodo(periodo)
    hoje = date.today()
    inicio = hoje - timedelta(days=dias)

    query = db.query(Reclamacao.data_reclamacao, func.count(Reclamacao.reclamacao_id).label("volume")).filter(
        Reclamacao.data_reclamacao >= inicio
    )
    if empresa_id:
        query = query.filter(Reclamacao.empresa_id == empresa_id)

    rows = query.group_by(Reclamacao.data_reclamacao).order_by(Reclamacao.data_reclamacao).all()
    return [EvolucaoItem(data=str(r.data_reclamacao), volume=r.volume) for r in rows]

@router.get("/ranking", response_model=List[RankingItem])
def ranking(periodo: str = "30d", limit: int = 10, db: Session = Depends(get_db), _=Depends(get_current_user)):
    dias = parse_periodo(periodo)
    hoje = date.today()
    inicio = hoje - timedelta(days=dias)
    inicio_ant = inicio - timedelta(days=dias)

    rows = db.query(
        Empresa.nome,
        func.count(Reclamacao.reclamacao_id).label("total")
    ).join(Reclamacao, Empresa.empresa_id == Reclamacao.empresa_id).filter(
        Reclamacao.data_reclamacao >= inicio
    ).group_by(Empresa.nome).order_by(func.count(Reclamacao.reclamacao_id).desc()).limit(limit).all()

    resultado = []
    for r in rows:
        total_ant = db.query(func.count(Reclamacao.reclamacao_id)).join(
            Empresa, Empresa.empresa_id == Reclamacao.empresa_id
        ).filter(
            Empresa.nome == r.nome,
            Reclamacao.data_reclamacao >= inicio_ant,
            Reclamacao.data_reclamacao < inicio
        ).scalar() or 0

        variacao = ((r.total - total_ant) / total_ant * 100) if total_ant > 0 else 0.0
        status = "critico" if variacao > 50 else "atencao" if variacao > 0 else "normal"
        resultado.append(RankingItem(empresa=r.nome, total=r.total, variacao=round(variacao, 2), status=status))

    return resultado

@router.get("/categorias", response_model=List[CategoriaItem])
def categorias(periodo: str = "30d", empresa_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    dias = parse_periodo(periodo)
    hoje = date.today()
    inicio = hoje - timedelta(days=dias)

    query = db.query(Reclamacao.categoria, func.count(Reclamacao.reclamacao_id).label("count")).filter(
        Reclamacao.data_reclamacao >= inicio
    )
    if empresa_id:
        query = query.filter(Reclamacao.empresa_id == empresa_id)

    rows = query.group_by(Reclamacao.categoria).order_by(func.count(Reclamacao.reclamacao_id).desc()).all()
    total = sum(r.count for r in rows)

    return [CategoriaItem(categoria=r.categoria, count=r.count, pct=round(r.count / total * 100, 2) if total > 0 else 0.0) for r in rows]
