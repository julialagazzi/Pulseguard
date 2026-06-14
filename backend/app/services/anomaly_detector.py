import statistics
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.reclamacao import Reclamacao
from ..models.alerta import Alerta
from ..models.empresa import Empresa

def detect_anomalies(db: Session, empresa_id: int, data_ref: date) -> Alerta | None:
    # Conta volume do dia de referência
    volume_dia = db.query(func.count(Reclamacao.reclamacao_id)).filter(
        Reclamacao.empresa_id == empresa_id,
        Reclamacao.data_reclamacao == data_ref
    ).scalar() or 0

    if volume_dia == 0:
        return None

    # Busca volumes dos 30 dias anteriores
    volumes_historicos = []
    for i in range(1, 31):
        d = data_ref - timedelta(days=i)
        vol = db.query(func.count(Reclamacao.reclamacao_id)).filter(
            Reclamacao.empresa_id == empresa_id,
            Reclamacao.data_reclamacao == d
        ).scalar() or 0
        volumes_historicos.append(vol)

    if len(volumes_historicos) < 2:
        return None

    media = statistics.mean(volumes_historicos)
    desvio = statistics.stdev(volumes_historicos) if len(volumes_historicos) > 1 else 0

    # Busca limiar da empresa
    empresa = db.query(Empresa).filter(Empresa.empresa_id == empresa_id).first()
    limiar = float(empresa.limiar_alerta_desvios) if empresa else 2.0

    if desvio == 0 or volume_dia <= media + (limiar * desvio):
        return None

    # Verifica se já existe alerta para este dia/empresa
    alerta_existente = db.query(Alerta).filter(
        Alerta.empresa_id == empresa_id,
        func.date(Alerta.data_deteccao) == data_ref
    ).first()
    if alerta_existente:
        return alerta_existente

    variacao_pct = ((volume_dia - media) / media * 100) if media > 0 else 0

    if variacao_pct < 100:
        severidade = "baixa"
    elif variacao_pct <= 200:
        severidade = "media"
    else:
        severidade = "alta"

    # Categoria dominante
    from ..models.reclamacao import Reclamacao as R
    cats = db.query(R.categoria, func.count(R.reclamacao_id).label("cnt")).filter(
        R.empresa_id == empresa_id,
        R.data_reclamacao == data_ref
    ).group_by(R.categoria).order_by(func.count(R.reclamacao_id).desc()).first()
    categoria_dominante = cats[0] if cats else "outros"

    alerta = Alerta(
        empresa_id=empresa_id,
        severidade=severidade,
        volume_dia=volume_dia,
        media_historica=round(media, 2),
        variacao_pct=round(variacao_pct, 2),
        categoria_dominante=categoria_dominante,
        status_alerta="ativo"
    )
    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    return alerta
