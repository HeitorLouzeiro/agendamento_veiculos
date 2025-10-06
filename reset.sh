#!/bin/bash

# ========================================
# Script de Reset do Banco de Dados
# Sistema de Agendamento de Veículos
# ========================================

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "========================================="
echo "  🗄️  RESET DO BANCO DE DADOS"
echo "     Sistema de Agendamento Veículos"
echo "========================================="
echo -e "${NC}"

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}[ERRO]${NC} manage.py não encontrado!"
    exit 1
fi

# Confirmar ação
echo -e "${YELLOW}⚠️  ATENÇÃO: Esta ação irá apagar TODOS os dados!${NC}"
echo -e "${YELLOW}Deseja continuar? [y/N]${NC}"
read -r response

if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${BLUE}[INFO]${NC} Operação cancelada."
    exit 0
fi

# Ativar ambiente virtual
echo -e "${BLUE}[INFO]${NC} Ativando ambiente virtual..."
source venv/bin/activate

# Remover banco de dados
if [ -f "db.sqlite3" ]; then
    echo -e "${BLUE}[INFO]${NC} Removendo banco de dados atual..."
    rm db.sqlite3
    echo -e "${GREEN}[SUCESSO]${NC} Banco removido!"
fi

# Remover arquivos de migração (exceto __init__.py)
echo -e "${BLUE}[INFO]${NC} Limpando migrações..."
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
echo -e "${GREEN}[SUCESSO]${NC} Migrações limpas!"

# Criar novas migrações
echo -e "${BLUE}[INFO]${NC} Criando novas migrações..."
python manage.py makemigrations usuarios
python manage.py makemigrations cursos
python manage.py makemigrations veiculos
python manage.py makemigrations agendamentos
python manage.py makemigrations dashboard

# Aplicar migrações
echo -e "${BLUE}[INFO]${NC} Aplicando migrações..."
python manage.py migrate

# Perguntar sobre dados de exemplo
echo -e "${BLUE}[INFO]${NC} Deseja carregar dados de exemplo? [Y/n]"
read -r data_response

if [[ ! "$data_response" =~ ^([nN][oO]|[nN])$ ]]; then
    echo -e "${BLUE}[INFO]${NC} Carregando dados de exemplo..."
    python manage.py load_sample_data
    echo -e "${GREEN}[SUCESSO]${NC} Dados carregados!"
    
    echo ""
    echo -e "${GREEN}✅ Reset completo realizado!${NC}"
    echo -e "${BLUE}[INFO]${NC} Credenciais de teste:"
    echo -e "${BLUE}[INFO]${NC} Admin: admin / admin123"
    echo -e "${BLUE}[INFO]${NC} Professor: prof01 / senha123"
else
    echo -e "${GREEN}✅ Reset do banco realizado!${NC}"
    echo -e "${YELLOW}[AVISO]${NC} Execute 'python manage.py createsuperuser' para criar um administrador."
fi

echo ""
echo -e "${GREEN}🚀 Para iniciar o servidor: ./start.sh${NC}"