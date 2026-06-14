import random
from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.usuario import Usuario
from ..models.empresa import Empresa
from ..models.reclamacao import Reclamacao
from ..utils.security import hash_password, require_role
from ..utils.checksum import sha256_text
from ..services.categorizer import categorize
from ..services.anomaly_detector import detect_anomalies

router = APIRouter(prefix="/seed", tags=["Seed"])

TEXTOS_RECLAMACOES = [
    "Fui cobrado indevidamente na minha fatura este mês, valor errado sem justificativa.",
    "Internet caiu novamente, já é a terceira vez esta semana sem sinal.",
    "Não consigo cancelar meu plano, o site não funciona e o atendimento demora.",
    "Péssimo atendimento, ficou mais de 1 hora esperando sem resolução.",
    "Cobrado duas vezes pelo mesmo serviço, preciso de reembolso urgente.",
    "Instabilidade na conexão desde segunda-feira, oscilação constante.",
    "Cancelei o contrato mas continuam me cobrando a fatura.",
    "Sem internet há dois dias, a equipe técnica não compareceu.",
    "Valor errado na fatura, não contratei este serviço adicional.",
    "Tempo de espera absurdo no atendimento, grosseria dos atendentes.",
    "Queda de sinal todos os dias no horário de pico.",
    "Estou tentando encerrar contrato há 30 dias sem sucesso.",
    "Duplicidade na cobrança do mês de janeiro.",
    "Sem sinal de internet, impactando meu trabalho home office.",
    "Mal atendido na loja, saí sem resolução do problema.",
]

@router.post("/")
def seed(db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    contagem = {"usuarios": 0, "empresas": 0, "reclamacoes": 0, "alertas": 0}

    # Usuários
    usuarios_seed = [
        ("Admin PulseGuard", "admin@pulseguard.com", "admin123", "admin"),
        ("Analista PulseGuard", "analista@pulseguard.com", "analista123", "analista"),
        ("Diretor PulseGuard", "diretor@pulseguard.com", "diretor123", "executivo"),
    ]
    for nome, email, senha, papel in usuarios_seed:
        if not db.query(Usuario).filter(Usuario.email == email).first():
            db.add(Usuario(nome=nome, email=email, senha_hash=hash_password(senha), papel=papel))
            contagem["usuarios"] += 1
    db.commit()

    # Empresas
    empresas_seed = [
        ("Vivo", "00000000000191", "telecomunicacoes"),
        ("Claro", "00000000000292", "telecomunicacoes"),
        ("TIM", "00000000000393", "telecomunicacoes"),
        ("Oi", "00000000000494", "telecomunicacoes"),
        ("Net/Claro", "00000000000595", "telecomunicacoes"),
    ]
    empresas_map = {}
    for nome, cnpj, setor in empresas_seed:
        emp = db.query(Empresa).filter(Empresa.cnpj == cnpj).first()
        if not emp:
            emp = Empresa(nome=nome, cnpj=cnpj, setor=setor)
            db.add(emp)
            db.flush()
            contagem["empresas"] += 1
        empresas_map[nome] = emp
    db.commit()

    hoje = date.today()
    empresas_datas = set()

    # Reclamações para Vivo — pico nos últimos 7 dias
    vivo = empresas_map["Vivo"]
    for i in range(120):
        if i < 80:
            # Últimos 7 dias (pico)
            dias_atras = random.randint(0, 6)
        else:
            # Dias anteriores (60 dias)
            dias_atras = random.randint(7, 60)
        data_rec = hoje - timedelta(days=dias_atras)
        texto = random.choice(TEXTOS_RECLAMACOES)
        checksum = sha256_text(texto + str(vivo.empresa_id) + str(data_rec) + str(i))
        if not db.query(Reclamacao).filter(Reclamacao.checksum_sha256 == checksum).first():
            db.add(Reclamacao(
                empresa_id=vivo.empresa_id,
                data_reclamacao=data_rec,
                categoria=categorize(texto),
                texto=texto,
                checksum_sha256=checksum
            ))
            empresas_datas.add((vivo.empresa_id, data_rec))
            contagem["reclamacoes"] += 1

    # Reclamações para Claro — 50 distribuídas normalmente
    claro = empresas_map["Claro"]
    for i in range(50):
        dias_atras = random.randint(0, 60)
        data_rec = hoje - timedelta(days=dias_atras)
        texto = random.choice(TEXTOS_RECLAMACOES)
        checksum = sha256_text(texto + str(claro.empresa_id) + str(data_rec) + str(i))
        if not db.query(Reclamacao).filter(Reclamacao.checksum_sha256 == checksum).first():
            db.add(Reclamacao(
                empresa_id=claro.empresa_id,
                data_reclamacao=data_rec,
                categoria=categorize(texto),
                texto=texto,
                checksum_sha256=checksum
            ))
            empresas_datas.add((claro.empresa_id, data_rec))
            contagem["reclamacoes"] += 1

    # Reclamações para TIM — 30 distribuídas normalmente
    tim = empresas_map["TIM"]
    for i in range(30):
        dias_atras = random.randint(0, 60)
        data_rec = hoje - timedelta(days=dias_atras)
        texto = random.choice(TEXTOS_RECLAMACOES)
        checksum = sha256_text(texto + str(tim.empresa_id) + str(data_rec) + str(i))
        if not db.query(Reclamacao).filter(Reclamacao.checksum_sha256 == checksum).first():
            db.add(Reclamacao(
                empresa_id=tim.empresa_id,
                data_reclamacao=data_rec,
                categoria=categorize(texto),
                texto=texto,
                checksum_sha256=checksum
            ))
            empresas_datas.add((tim.empresa_id, data_rec))
            contagem["reclamacoes"] += 1

    db.commit()

    # Detecta anomalias
    for emp_id, data_ref in empresas_datas:
        alerta = detect_anomalies(db, emp_id, data_ref)
        if alerta:
            contagem["alertas"] += 1

    return {"inseridos": contagem}
