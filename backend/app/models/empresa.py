from sqlalchemy import Column, Integer, String, Boolean, Numeric
from ..database import Base

class Empresa(Base):
    __tablename__ = "empresas"

    empresa_id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    cnpj = Column(String(14), unique=True, nullable=False)
    setor = Column(String(50), nullable=False)
    limiar_alerta_desvios = Column(Numeric(3, 1), default=2.0)
    ativa = Column(Boolean, default=True)
