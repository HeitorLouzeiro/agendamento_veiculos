#!/bin/bash

# ========================================
# Script para Iniciar Containers Docker
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
echo "  🚀 INICIANDO CONTAINERS DOCKER"
echo "========================================="
echo -e "${NC}"

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo -e "${RED}[ERRO]${NC} Arquivo .env não encontrado!"
    echo -e "${YELLOW}[AVISO]${NC} Execute primeiro: ${GREEN}./docker-setup.sh${NC}"
    exit 1
fi

# Verificar se o Docker está rodando
if ! docker info &> /dev/null; then
    echo -e "${RED}[ERRO]${NC} Docker não está em execução!"
    echo -e "${YELLOW}[AVISO]${NC} Inicie o serviço do Docker primeiro"
    exit 1
fi

# Perguntar qual modo
echo -e "${BLUE}[INFO]${NC} Escolha o modo de execução:"
echo -e "  ${GREEN}1${NC} - Produção (Gunicorn)"
echo -e "  ${GREEN}2${NC} - Desenvolvimento (Runserver com live reload)"
echo -e "  ${GREEN}3${NC} - Modo detached (background)"
read -p "Opção [1]: " modo
modo=${modo:-1}

case $modo in
    1)
        echo -e "${BLUE}[INFO]${NC} Iniciando em modo produção..."
        docker compose up web
        ;;
    2)
        echo -e "${BLUE}[INFO]${NC} Iniciando em modo desenvolvimento..."
        docker compose up web-dev
        ;;
    3)
        echo -e "${BLUE}[INFO]${NC} Iniciando containers em background..."
        docker compose up -d
        echo -e "${GREEN}[SUCESSO]${NC} Containers iniciados!"
        echo -e "${BLUE}[INFO]${NC} Acesse: ${GREEN}http://localhost:8000${NC}"
        echo -e "${BLUE}[INFO]${NC} Ver logs: ${GREEN}docker compose logs -f${NC}"
        ;;
    *)
        echo -e "${RED}[ERRO]${NC} Opção inválida!"
        exit 1
        ;;
esac
