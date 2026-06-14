from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base

class Relatorio(Base):
    __tablename__ = "relatorios"

    relatorio_id = Column(Integer, primary_key=True, autoincrement=True)
    alerta_id = Column(Integer, ForeignKey("alertas.alerta_id"), nullable=False)
    gerado_por = Column(Integer, ForeignKey("usuarios.usuario_id"), nullable=False)
    tipo = Column(String(20), default="manual")
    caminho_arquivo = Column(String(255), nullable=False)
    criado_em = Column(DateTime, default=func.now())
