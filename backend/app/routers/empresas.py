from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.empresa import Empresa
from ..schemas.empresa import EmpresaCreate, EmpresaUpdate, EmpresaResponse
from ..utils.security import get_current_user, require_role

router = APIRouter(prefix="/empresas", tags=["Empresas"])

@router.get("/", response_model=List[EmpresaResponse])
def listar_empresas(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Empresa).filter(Empresa.ativa == True).all()

@router.post("/", response_model=EmpresaResponse)
def criar_empresa(
    data: EmpresaCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin"))
):
    if db.query(Empresa).filter(Empresa.cnpj == data.cnpj).first():
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado")
    empresa = Empresa(**data.model_dump())
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return empresa

@router.get("/{empresa_id}", response_model=EmpresaResponse)
def detalhe_empresa(empresa_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    empresa = db.query(Empresa).filter(Empresa.empresa_id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa

@router.put("/{empresa_id}", response_model=EmpresaResponse)
def atualizar_empresa(
    empresa_id: int,
    data: EmpresaUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin"))
):
    empresa = db.query(Empresa).filter(Empresa.empresa_id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(empresa, key, val)
    db.commit()
    db.refresh(empresa)
    return empresa

@router.delete("/{empresa_id}")
def deletar_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin"))
):
    empresa = db.query(Empresa).filter(Empresa.empresa_id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    empresa.ativa = False
    db.commit()
    return {"detail": "Empresa desativada"}
