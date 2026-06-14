from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..database import Base

class Importacao(Base):
    __tablename__ = "importacoes"

    importacao_id = Column(Integer, primary_key=True, autoincrement=True)
    nome_arquivo = Column(String(255), nullable=False)
    total_registros = Column(Integer, default=0)
    total_erros = Column(Integer, default=0)
    checksum_sha256 = Column(String(64), nullable=False)
    importado_em = Column(DateTime, default=func.now())
