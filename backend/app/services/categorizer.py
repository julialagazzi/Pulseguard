KEYWORDS = {
    "cobranca_indevida": ["cobrado", "cobrança", "fatura", "indevido", "valor errado",
                          "cobrado duas vezes", "duplicidade", "não contratei"],
    "falha_servico": ["queda", "sem sinal", "internet caiu", "instabilidade", "lento",
                      "não funciona", "sem internet", "oscilação"],
    "cancelamento": ["cancelar", "cancelamento", "rescisão", "cancelei", "desistir",
                     "encerrar contrato", "não consigo cancelar"],
    "atendimento": ["atendimento", "tempo de espera", "grosseria", "mal atendido",
                    "sem resposta", "demora", "péssimo atendimento"],
}

def categorize(texto: str) -> str:
    texto_lower = texto.lower()
    scores = {cat: sum(1 for kw in kws if kw in texto_lower)
              for cat, kws in KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "outros"
