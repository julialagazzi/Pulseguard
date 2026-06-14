import io
from datetime import date
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
from ..database import get_db
from ..models.reclamacao import Reclamacao
from ..models.empresa import Empresa
from ..models.importacao import Importacao
from ..schemas.reclamacao import ReclamacaoResponse
from ..utils.security import get_current_user, require_role
from ..utils.checksum import sha256_text, sha256_file
from ..services.categorizer import categorize
from ..services.anomaly_detector import detect_anomalies

router = APIRouter(prefix="/reclamacoes", tags=["Reclamações"])

@router.post("/import")
def importar_csv(
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "analista"))
):
    conteudo = arquivo.file.read()
    checksum_arquivo = sha256_file(conteudo)

    try:
        df = pd.read_csv(io.StringIO(conteudo.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler CSV: {str(e)}")

    importacao = Importacao(
        nome_arquivo=arquivo.filename,
        checksum_sha256=checksum_arquivo
    )
    db.add(importacao)
    db.flush()

    importados, ignorados, erros = 0, 0, 0
    empresas_datas = set()

    for _, row in df.iterrows():
        try:
            empresa = db.query(Empresa).filter(Empresa.cnpj == str(row["empresa_cnpj"])).first()
            if not empresa:
                erros += 1
                continue

            checksum = sha256_text(str(row["texto"]))
            if db.query(Reclamacao).filter(Reclamacao.checksum_sha256 == checksum).first():
                ignorados += 1
                continue

            categoria = categorize(str(row["texto"]))
            data_rec = pd.to_datetime(row["data_reclamacao"]).date()

            rec = Reclamacao(
                empresa_id=empresa.empresa_id,
                importacao_id=importacao.importacao_id,
                data_reclamacao=data_rec,
                categoria=categoria,
                texto=str(row["texto"]),
                status=str(row.get("status", "aberta")),
                checksum_sha256=checksum
            )
            db.add(rec)
            importados += 1
            empresas_datas.add((empresa.empresa_id, data_rec))
        except Exception:
            erros += 1

    importacao.total_registros = importados + ignorados
    importacao.total_erros = erros
    db.commit()

    # Detecta anomalias para cada empresa/data
    for emp_id, data_ref in empresas_datas:
        detect_anomalies(db, emp_id, data_ref)

    return {"importados": importados, "ignorados": ignorados, "erros": erros, "checksum_arquivo": checksum_arquivo}

@router.get("/", response_model=List[ReclamacaoResponse])
def listar_reclamacoes(
    empresa_id: Optional[int] = None,
    categoria: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    query = db.query(Reclamacao)
    if empresa_id:
        query = query.filter(Reclamacao.empresa_id == empresa_id)
    if categoria:
        query = query.filter(Reclamacao.categoria == categoria)
    if data_inicio:
        query = query.filter(Reclamacao.data_reclamacao >= data_inicio)
    if data_fim:
        query = query.filter(Reclamacao.data_reclamacao <= data_fim)
    return query.offset((page - 1) * size).limit(size).all()
