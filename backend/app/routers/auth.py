from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.usuario import Usuario
from ..utils.security import (
    verify_password, create_access_token, get_current_user, verify_token
)
from ..schemas.usuario import UsuarioResponse
from ..config import settings

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    # Verifica bloqueio
    if usuario.bloqueado_ate and usuario.bloqueado_ate > datetime.utcnow():
        raise HTTPException(status_code=403, detail="Conta bloqueada temporariamente")

    if not verify_password(form_data.password, usuario.senha_hash):
        usuario.tentativas_login = (usuario.tentativas_login or 0) + 1
        if usuario.tentativas_login >= 5:
            usuario.bloqueado_ate = datetime.utcnow() + timedelta(minutes=15)
        db.commit()
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    # Login bem-sucedido
    usuario.tentativas_login = 0
    usuario.bloqueado_ate = None
    db.commit()

    token = create_access_token({"sub": usuario.email, "papel": usuario.papel})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/refresh")
def refresh_token(current_user: Usuario = Depends(get_current_user)):
    token = create_access_token({"sub": current_user.email, "papel": current_user.papel})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UsuarioResponse)
def me(current_user: Usuario = Depends(get_current_user)):
    return current_user
