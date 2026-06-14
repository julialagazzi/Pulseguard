CREATE TABLE IF NOT EXISTS usuarios (
    usuario_id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    papel VARCHAR(20) NOT NULL CHECK (papel IN ('admin', 'analista', 'executivo')),
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT NOW(),
    tentativas_login INTEGER DEFAULT 0,
    bloqueado_ate TIMESTAMP
);

CREATE TABLE IF NOT EXISTS empresas (
    empresa_id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    cnpj VARCHAR(14) UNIQUE NOT NULL,
    setor VARCHAR(50) NOT NULL,
    limiar_alerta_desvios NUMERIC(3,1) DEFAULT 2.0,
    ativa BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS importacoes (
    importacao_id SERIAL PRIMARY KEY,
    nome_arquivo VARCHAR(255) NOT NULL,
    total_registros INTEGER DEFAULT 0,
    total_erros INTEGER DEFAULT 0,
    checksum_sha256 VARCHAR(64) NOT NULL,
    importado_em TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reclamacoes (
    reclamacao_id SERIAL PRIMARY KEY,
    empresa_id INTEGER NOT NULL REFERENCES empresas(empresa_id),
    importacao_id INTEGER REFERENCES importacoes(importacao_id),
    data_reclamacao DATE NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    texto TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'aberta',
    checksum_sha256 VARCHAR(64) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS alertas (
    alerta_id SERIAL PRIMARY KEY,
    empresa_id INTEGER NOT NULL REFERENCES empresas(empresa_id),
    data_deteccao TIMESTAMP DEFAULT NOW(),
    severidade VARCHAR(10) NOT NULL CHECK (severidade IN ('baixa', 'media', 'alta')),
    volume_dia INTEGER NOT NULL,
    media_historica NUMERIC(8,2) NOT NULL,
    variacao_pct NUMERIC(6,2) NOT NULL,
    categoria_dominante VARCHAR(50) NOT NULL,
    status_alerta VARCHAR(20) DEFAULT 'ativo'
);

CREATE TABLE IF NOT EXISTS relatorios (
    relatorio_id SERIAL PRIMARY KEY,
    alerta_id INTEGER NOT NULL REFERENCES alertas(alerta_id),
    gerado_por INTEGER NOT NULL REFERENCES usuarios(usuario_id),
    tipo VARCHAR(20) DEFAULT 'manual',
    caminho_arquivo VARCHAR(255) NOT NULL,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- Índices de performance
CREATE INDEX IF NOT EXISTS idx_reclamacoes_empresa_data ON reclamacoes(empresa_id, data_reclamacao);
CREATE INDEX IF NOT EXISTS idx_reclamacoes_categoria ON reclamacoes(categoria);
CREATE INDEX IF NOT EXISTS idx_alertas_empresa ON alertas(empresa_id);
CREATE INDEX IF NOT EXISTS idx_alertas_status ON alertas(status_alerta);
