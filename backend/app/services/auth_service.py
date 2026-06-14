from sqlalchemy.orm import Session
from ..models.usuario import Usuario
from ..utils.security import verify_password, hash_password

def authenticate_user(db: Session, email: str, password: str) -> Usuario | None:
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return None
    if not verify_password(password, usuario.senha_hash):
        return None
    return usuario
