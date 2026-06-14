from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.sql import func
from ..database import Base

class Alerta(Base):
    __tablename__ = "alertas"

    alerta_id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_id = Column(Integer, ForeignKey("empresas.empresa_id"), nullable=False)
    data_deteccao = Column(DateTime, default=func.now())
    severidade = Column(String(10), nullable=False)  # baixa/media/alta
    volume_dia = Column(Integer, nullable=False)
    media_historica = Column(Numeric(8, 2), nullable=False)
    variacao_pct = Column(Numeric(6, 2), nullable=False)
    categoria_dominante = Column(String(50), nullable=False)
    status_alerta = Column(String(20), default="ativo")
