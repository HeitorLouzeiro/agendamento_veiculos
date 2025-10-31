#!/bin/bash

# ========================================
# Script para Ver Logs dos Containers
# Sistema de Agendamento de Veículos
# ========================================

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}"
echo "========================================="
echo "  📋 LOGS DOS CONTAINERS"
echo "========================================="
echo -e "${NC}"

echo -e "${BLUE}[INFO]${NC} Escolha qual log visualizar:"
echo -e "  ${GREEN}1${NC} - Todos os containers"
echo -e "  ${GREEN}2${NC} - Apenas aplicação web"
echo -e "  ${GREEN}3${NC} - Apenas PostgreSQL"
read -p "Opção [1]: " opcao
opcao=${opcao:-1}

case $opcao in
    1)
        echo -e "${BLUE}[INFO]${NC} Exibindo logs de todos os containers..."
        docker compose logs -f
        ;;
    2)
        echo -e "${BLUE}[INFO]${NC} Exibindo logs da aplicação web..."
        docker compose logs -f web
        ;;
    3)
        echo -e "${BLUE}[INFO]${NC} Exibindo logs do PostgreSQL..."
        docker compose logs -f db
        ;;
    *)
        echo -e "${RED}[ERRO]${NC} Opção inválida!"
        exit 1
        ;;
esac
