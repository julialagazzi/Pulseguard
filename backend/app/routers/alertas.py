from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.alerta import Alerta
from ..models.empresa import Empresa
from ..models.reclamacao import Reclamacao
from ..schemas.alerta import AlertaResponse
from ..utils.security import get_current_user
from ..services.pdf_generator import ACOES_SUGERIDAS

router = APIRouter(prefix="/alertas", tags=["Alertas"])

@router.get("/", response_model=List[AlertaResponse])
def listar_alertas(
    empresa_id: Optional[int] = None,
    severidade: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    query = db.query(Alerta)
    if empresa_id:
        query = query.filter(Alerta.empresa_id == empresa_id)
    if severidade:
        query = query.filter(Alerta.severidade == severidade)
    if status:
        query = query.filter(Alerta.status_alerta == status)
    return query.order_by(Alerta.data_deteccao.desc()).all()

@router.get("/{alerta_id}")
def detalhe_alerta(alerta_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    alerta = db.query(Alerta).filter(Alerta.alerta_id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")

    empresa = db.query(Empresa).filter(Empresa.empresa_id == alerta.empresa_id).first()

    from sqlalchemy import func
    amostras = db.query(Reclamacao).filter(
        Reclamacao.empresa_id == alerta.empresa_id,
        func.date(Reclamacao.data_reclamacao) == func.date(alerta.data_deteccao)
    ).limit(5).all()

    acoes = ACOES_SUGERIDAS.get(alerta.categoria_dominante, ["Analisar causa raiz"])

    return {
        "alerta": alerta,
        "empresa": empresa,
        "amostras_reclamacoes": amostras,
        "acoes_sugeridas": acoes
    }

@router.post("/{alerta_id}/resolver")
def resolver_alerta(alerta_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    alerta = db.query(Alerta).filter(Alerta.alerta_id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    alerta.status_alerta = "resolvido"
    db.commit()
    return {"detail": "Alerta marcado como resolvido"}
