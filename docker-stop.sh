#!/bin/bash

# ========================================
# Script para Parar Containers Docker
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
echo "  🛑 PARANDO CONTAINERS DOCKER"
echo "========================================="
echo -e "${NC}"

# Parar todos os containers
echo -e "${BLUE}[INFO]${NC} Parando containers..."
docker compose down

echo -e "${GREEN}[SUCESSO]${NC} Containers parados!"
echo ""
echo -e "${BLUE}[INFO]${NC} Para remover também os volumes: ${GREEN}docker compose down -v${NC}"
