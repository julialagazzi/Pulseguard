from fpdf import FPDF
from datetime import date

ACOES_SUGERIDAS = {
    "cobranca_indevida": [
        "Notificar equipe de faturamento",
        "Verificar sistema de cobranças",
        "Contatar clientes afetados"
    ],
    "falha_servico": [
        "Acionar equipe técnica NOC",
        "Verificar infraestrutura da região",
        "Comunicar previsão de resolução"
    ],
    "cancelamento": [
        "Revisar processo de cancelamento",
        "Treinar equipe de retenção"
    ],
    "atendimento": [
        "Realizar treinamento de equipe",
        "Revisar filas de atendimento"
    ],
}

def generate_crisis_report(alerta, empresa, reclamacoes_amostra: list) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "PulseGuard - Relatorio de Crise", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Gerado em: {date.today().strftime('%d/%m/%Y')}", ln=True, align="C")
    pdf.ln(5)

    # Seção 1: Resumo
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "1. Resumo", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Empresa: {empresa.nome}", ln=True)
    pdf.cell(0, 7, f"Severidade: {alerta.severidade.upper()}", ln=True)
    pdf.cell(0, 7, f"Variacao: {float(alerta.variacao_pct):.1f}%", ln=True)
    pdf.cell(0, 7, f"Data de deteccao: {alerta.data_deteccao}", ln=True)
    pdf.ln(3)

    # Seção 2: Métricas
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "2. Metricas", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Volume no dia: {alerta.volume_dia}", ln=True)
    pdf.cell(0, 7, f"Media historica: {float(alerta.media_historica):.2f}", ln=True)
    pdf.cell(0, 7, f"Categoria dominante: {alerta.categoria_dominante}", ln=True)
    pdf.ln(3)

    # Seção 3: Amostras de Reclamações
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "3. Amostras de Reclamacoes", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for i, rec in enumerate(reclamacoes_amostra[:5], 1):
        texto = rec.texto[:200] + "..." if len(rec.texto) > 200 else rec.texto
        pdf.multi_cell(0, 6, f"{i}. {texto}")
        pdf.ln(1)
    pdf.ln(3)

    # Seção 4: Ações Sugeridas
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "4. Acoes Sugeridas", ln=True)
    pdf.set_font("Helvetica", "", 11)
    acoes = ACOES_SUGERIDAS.get(alerta.categoria_dominante, ["Analisar causa raiz", "Comunicar equipes responsaveis"])
    for acao in acoes:
        pdf.cell(0, 7, f"  - {acao}", ln=True)

    return bytes(pdf.output())
