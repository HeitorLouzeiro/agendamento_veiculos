#!/bin/bash

# ========================================
# Script para Reset Completo Docker
# Sistema de Agendamento de Veículos
# ========================================

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${RED}"
echo "========================================="
echo "  ⚠️  RESET COMPLETO DOCKER"
echo "     ISTO VAI APAGAR TODOS OS DADOS!"
echo "========================================="
echo -e "${NC}"

read -p "Tem certeza que deseja continuar? Digite 'SIM' para confirmar: " confirmacao

if [ "$confirmacao" != "SIM" ]; then
    echo -e "${YELLOW}[CANCELADO]${NC} Operação cancelada pelo usuário"
    exit 0
fi

echo -e "${BLUE}[INFO]${NC} Parando todos os containers..."
docker compose down

echo -e "${BLUE}[INFO]${NC} Removendo volumes..."
docker compose down -v

echo -e "${BLUE}[INFO]${NC} Removendo imagens antigas..."
docker compose rm -f

echo -e "${GREEN}[SUCESSO]${NC} Reset completo executado!"
echo ""
echo -e "${BLUE}[INFO]${NC} Execute novamente: ${GREEN}./docker-setup.sh${NC}"
