import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.alerta import Alerta
from ..models.empresa import Empresa
from ..models.reclamacao import Reclamacao
from ..models.relatorio import Relatorio
from ..utils.security import get_current_user
from ..services.pdf_generator import generate_crisis_report
from sqlalchemy import func

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])

RELATORIOS_DIR = "/app/relatorios"

@router.post("/gerar/{alerta_id}")
def gerar_relatorio(
    alerta_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    alerta = db.query(Alerta).filter(Alerta.alerta_id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")

    empresa = db.query(Empresa).filter(Empresa.empresa_id == alerta.empresa_id).first()

    amostras = db.query(Reclamacao).filter(
        Reclamacao.empresa_id == alerta.empresa_id,
        func.date(Reclamacao.data_reclamacao) == func.date(alerta.data_deteccao)
    ).limit(5).all()

    pdf_bytes = generate_crisis_report(alerta, empresa, amostras)

    os.makedirs(RELATORIOS_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{alerta_id}_{timestamp}.pdf"
    caminho = os.path.join(RELATORIOS_DIR, nome_arquivo)

    with open(caminho, "wb") as f:
        f.write(pdf_bytes)

    relatorio = Relatorio(
        alerta_id=alerta_id,
        gerado_por=current_user.usuario_id,
        caminho_arquivo=caminho
    )
    db.add(relatorio)
    db.commit()

    return FileResponse(caminho, media_type="application/pdf", filename=nome_arquivo)

@router.get("/")
def listar_relatorios(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Relatorio).order_by(Relatorio.criado_em.desc()).all()
