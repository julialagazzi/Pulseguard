from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from ..database import Base

class Reclamacao(Base):
    __tablename__ = "reclamacoes"

    reclamacao_id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_id = Column(Integer, ForeignKey("empresas.empresa_id"), nullable=False)
    importacao_id = Column(Integer, ForeignKey("importacoes.importacao_id"), nullable=True)
    data_reclamacao = Column(Date, nullable=False)
    categoria = Column(String(50), nullable=False)
    texto = Column(Text, nullable=False)
    status = Column(String(20), default="aberta")
    checksum_sha256 = Column(String(64), unique=True, nullable=False)
