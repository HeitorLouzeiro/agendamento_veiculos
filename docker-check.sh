#!/bin/bash

# ========================================
# Script de Verificação do Ambiente Docker
# Sistema de Agendamento de Veículos
# ========================================

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}"
echo "========================================="
echo "  🔍 VERIFICAÇÃO DO AMBIENTE"
echo "========================================="
echo -e "${NC}"

# Função para verificar comando
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}[✓]${NC} $2 encontrado"
        return 0
    else
        echo -e "${RED}[✗]${NC} $2 não encontrado"
        return 1
    fi
}

# Verificar Docker
echo -e "${BLUE}[INFO]${NC} Verificando Docker..."
if check_command docker "Docker"; then
    docker --version
else
    echo -e "${YELLOW}[AVISO]${NC} Instale: https://docs.docker.com/get-docker/"
fi
echo ""

# Verificar Docker Compose
echo -e "${BLUE}[INFO]${NC} Verificando Docker Compose..."
if docker compose version &> /dev/null; then
    echo -e "${GREEN}[✓]${NC} Docker Compose encontrado"
    docker compose version
else
    echo -e "${RED}[✗]${NC} Docker Compose não encontrado"
    echo -e "${YELLOW}[AVISO]${NC} Instale: https://docs.docker.com/compose/install/"
fi
echo ""

# Verificar se Docker está rodando
echo -e "${BLUE}[INFO]${NC} Verificando se Docker está em execução..."
if docker info &> /dev/null; then
    echo -e "${GREEN}[✓]${NC} Docker está rodando"
else
    echo -e "${RED}[✗]${NC} Docker não está rodando"
    echo -e "${YELLOW}[AVISO]${NC} Inicie o serviço do Docker"
fi
echo ""

# Verificar arquivo .env
echo -e "${BLUE}[INFO]${NC} Verificando arquivo .env..."
if [ -f ".env" ]; then
    echo -e "${GREEN}[✓]${NC} Arquivo .env encontrado"
    
    # Verificar variáveis importantes
    if grep -q "DB_ENGINE=postgresql" .env; then
        echo -e "${GREEN}[✓]${NC} DB_ENGINE configurado para PostgreSQL"
    else
        echo -e "${YELLOW}[⚠]${NC} DB_ENGINE não está como postgresql"
    fi
    
    if grep -q "SECRET_KEY=" .env; then
        echo -e "${GREEN}[✓]${NC} SECRET_KEY definida"
    else
        echo -e "${RED}[✗]${NC} SECRET_KEY não definida"
    fi
else
    echo -e "${RED}[✗]${NC} Arquivo .env não encontrado"
    echo -e "${YELLOW}[AVISO]${NC} Execute: ./docker-setup.sh"
fi
echo ""

# Verificar containers
echo -e "${BLUE}[INFO]${NC} Verificando containers Docker..."
if docker compose ps &> /dev/null; then
    CONTAINERS=$(docker compose ps --format "table {{.Service}}\t{{.State}}\t{{.Status}}")
    if [ -z "$CONTAINERS" ]; then
        echo -e "${YELLOW}[⚠]${NC} Nenhum container em execução"
        echo -e "${BLUE}[INFO]${NC} Execute: ./docker-start.sh"
    else
        echo -e "${GREEN}[✓]${NC} Containers encontrados:"
        echo "$CONTAINERS"
    fi
else
    echo -e "${YELLOW}[⚠]${NC} Não foi possível verificar containers"
fi
echo ""

# Verificar imagens
echo -e "${BLUE}[INFO]${NC} Verificando imagens Docker..."
if docker images | grep -q "agendamento_veiculos"; then
    echo -e "${GREEN}[✓]${NC} Imagens do projeto encontradas"
else
    echo -e "${YELLOW}[⚠]${NC} Imagens não construídas"
    echo -e "${BLUE}[INFO]${NC} Execute: ./docker-setup.sh"
fi
echo ""

# Verificar volumes
echo -e "${BLUE}[INFO]${NC} Verificando volumes Docker..."
VOLUMES=$(docker volume ls | grep agendamento)
if [ -n "$VOLUMES" ]; then
    echo -e "${GREEN}[✓]${NC} Volumes encontrados:"
    echo "$VOLUMES"
else
    echo -e "${YELLOW}[⚠]${NC} Nenhum volume encontrado"
fi
echo ""

# Testar conexão com PostgreSQL (se estiver rodando)
echo -e "${BLUE}[INFO]${NC} Testando conexão com PostgreSQL..."
if docker compose ps | grep -q "db.*running"; then
    if docker compose exec -T db pg_isready -U postgres &> /dev/null; then
        echo -e "${GREEN}[✓]${NC} PostgreSQL está acessível"
        
        # Verificar banco de dados
        DB_EXISTS=$(docker compose exec -T db psql -U postgres -lqt | cut -d \| -f 1 | grep -w agendamento_veiculos)
        if [ -n "$DB_EXISTS" ]; then
            echo -e "${GREEN}[✓]${NC} Banco 'agendamento_veiculos' existe"
        else
            echo -e "${RED}[✗]${NC} Banco 'agendamento_veiculos' não existe"
        fi
    else
        echo -e "${RED}[✗]${NC} PostgreSQL não está respondendo"
    fi
else
    echo -e "${YELLOW}[⚠]${NC} Container PostgreSQL não está rodando"
fi
echo ""

# Verificar aplicação web
echo -e "${BLUE}[INFO]${NC} Verificando aplicação web..."
if docker compose ps | grep -q "web.*running"; then
    echo -e "${GREEN}[✓]${NC} Container web está rodando"
    
    # Testar se está respondendo
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo -e "${GREEN}[✓]${NC} Aplicação está acessível em http://localhost:8000"
    else
        echo -e "${YELLOW}[⚠]${NC} Aplicação pode estar iniciando ou com erro"
        echo -e "${BLUE}[INFO]${NC} Verifique os logs: docker compose logs -f web"
    fi
else
    echo -e "${YELLOW}[⚠]${NC} Container web não está rodando"
fi
echo ""

# Verificar portas
echo -e "${BLUE}[INFO]${NC} Verificando portas..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 || ss -ltn | grep -q :8000; then
    echo -e "${GREEN}[✓]${NC} Porta 8000 está em uso (aplicação web)"
else
    echo -e "${YELLOW}[⚠]${NC} Porta 8000 está livre"
fi

if lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1 || ss -ltn | grep -q :5432; then
    echo -e "${GREEN}[✓]${NC} Porta 5432 está em uso (PostgreSQL)"
else
    echo -e "${YELLOW}[⚠]${NC} Porta 5432 está livre"
fi
echo ""

# Espaço em disco
echo -e "${BLUE}[INFO]${NC} Espaço usado pelo Docker..."
docker system df 2>/dev/null || echo -e "${YELLOW}[⚠]${NC} Não foi possível verificar"
echo ""

# Resumo
echo -e "${PURPLE}"
echo "========================================="
echo "  📊 RESUMO"
echo "========================================="
echo -e "${NC}"

if docker info &> /dev/null && [ -f ".env" ]; then
    if docker compose ps | grep -q "running"; then
        echo -e "${GREEN}[✓] Sistema está pronto e rodando!${NC}"
        echo -e "${BLUE}[INFO]${NC} Acesse: ${GREEN}http://localhost:8000${NC}"
    else
        echo -e "${YELLOW}[⚠] Docker está OK, mas containers não estão rodando${NC}"
        echo -e "${BLUE}[INFO]${NC} Execute: ${GREEN}./docker-start.sh${NC}"
    fi
else
    echo -e "${RED}[✗] Sistema não está pronto${NC}"
    echo -e "${BLUE}[INFO]${NC} Execute: ${GREEN}./docker-setup.sh${NC}"
fi
echo ""
