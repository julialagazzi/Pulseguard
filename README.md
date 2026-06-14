# PulseGuard

Sistema de Monitoramento e Análise de Reclamações do Consumidor.

## Pré-requisito
Docker Desktop instalado: https://www.docker.com/products/docker-desktop/

## Como rodar em 4 passos

```bash
# 1. Copie o arquivo de configuração
cp .env.example .env

# 2. Edite o .env e troque as senhas pelos seus próprios valores

# 3. Suba os serviços
docker-compose up --build -d

# 4. Aguarde ~30 segundos e popule com dados demo
# Primeiro faça login para obter o token:
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@pulseguard.com&password=admin123"

# Use o access_token retornado:
curl -X POST http://localhost:8000/api/v1/seed/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## Acessos
- Documentação da API: http://localhost:8000/docs
- Credenciais: admin@pulseguard.com / admin123

## Arquitetura
Browser → React (Lovable) → FastAPI (8000) → PostgreSQL (5432 interno)
Todos os serviços na rede Docker interna pulseguard-net.
