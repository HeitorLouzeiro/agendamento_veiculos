#!/bin/bash

# Script de desenvolvimento rápido - versão simples
# Para uso: ./dev.sh

echo "🚀 Iniciando desenvolvimento rápido..."

# Ativar venv e executar
source venv/bin/activate
python manage.py migrate
python manage.py runserver 8000