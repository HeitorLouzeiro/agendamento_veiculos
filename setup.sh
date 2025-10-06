#!/bin/bash

# ========================================
# Script de Setup Inicial
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
echo "  🛠️  SETUP INICIAL DO PROJETO"
echo "     Sistema de Agendamento Veículos"
echo "========================================="
echo -e "${NC}"

# Verificar Python
echo -e "${BLUE}[INFO]${NC} Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERRO]${NC} Python3 não encontrado!"
    exit 1
fi
echo -e "${GREEN}[SUCESSO]${NC} Python3 encontrado: $(python3 --version)"

# Verificar pip
echo -e "${BLUE}[INFO]${NC} Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}[ERRO]${NC} pip3 não encontrado!"
    exit 1
fi
echo -e "${GREEN}[SUCESSO]${NC} pip3 encontrado"

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo -e "${BLUE}[INFO]${NC} Criando ambiente virtual..."
    python3 -m venv venv
    echo -e "${GREEN}[SUCESSO]${NC} Ambiente virtual criado!"
else
    echo -e "${YELLOW}[AVISO]${NC} Ambiente virtual já existe"
fi

# Ativar ambiente virtual
echo -e "${BLUE}[INFO]${NC} Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo -e "${BLUE}[INFO]${NC} Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo -e "${BLUE}[INFO]${NC} Instalando dependências..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}[SUCESSO]${NC} Dependências instaladas!"
else
    echo -e "${RED}[ERRO]${NC} requirements.txt não encontrado!"
    exit 1
fi

# Verificar se manage.py existe
if [ ! -f "manage.py" ]; then
    echo -e "${RED}[ERRO]${NC} manage.py não encontrado!"
    exit 1
fi

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo -e "${BLUE}[INFO]${NC} Criando arquivo .env..."
    cat > .env << 'EOF'
# ========================================
# Variáveis de Ambiente - Desenvolvimento
# Sistema de Agendamento de Veículos
# ========================================

# Segurança (OBRIGATÓRIO em produção)
SECRET_KEY=sua-chave-secreta-super-segura-aqui-mude-em-producao

# Modo de desenvolvimento
DEBUG=True

# Hosts permitidos (separados por vírgula)
ALLOWED_HOSTS=localhost,127.0.0.1

# Configurações regionais
TIME_ZONE=America/Sao_Paulo
LANGUAGE_CODE=pt-br
EOF
    echo -e "${GREEN}[SUCESSO]${NC} Arquivo .env criado!"
    echo -e "${BLUE}[INFO]${NC} Configurações de desenvolvimento prontas para uso."
else
    echo -e "${YELLOW}[AVISO]${NC} Arquivo .env já existe, mantendo configurações existentes"
fi

# Executar migrações
echo -e "${BLUE}[INFO]${NC} Executando migrações..."
python manage.py migrate

# Verificar se existem usuários
echo -e "${BLUE}[INFO]${NC} Verificando usuários existentes..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if User.objects.filter(is_superuser=True).exists():
    print('SUPERUSER_EXISTS')
else:
    print('NO_SUPERUSER')
" > /tmp/user_check 2>/dev/null

if grep -q "NO_SUPERUSER" /tmp/user_check; then
    echo -e "${YELLOW}[AVISO]${NC} Nenhum superusuário encontrado."
    echo -e "${BLUE}[INFO]${NC} Carregando dados de exemplo..."
    python manage.py load_sample_data
    echo -e "${GREEN}[SUCESSO]${NC} Dados de exemplo carregados!"
else
    echo -e "${GREEN}[SUCESSO]${NC} Superusuário já existe!"
fi

rm -f /tmp/user_check

# Tornar scripts executáveis
echo -e "${BLUE}[INFO]${NC} Configurando permissões dos scripts..."
chmod +x start.sh dev.sh reset.sh setup.sh

echo ""
echo -e "${GREEN}✅ SETUP COMPLETO!${NC}"
echo ""
echo -e "${PURPLE}📋 Próximos passos:${NC}"
echo -e "${BLUE}[INFO]${NC} 1. Execute: ${GREEN}./start.sh${NC} (iniciar servidor completo)"
echo -e "${BLUE}[INFO]${NC} 2. Ou execute: ${GREEN}./dev.sh${NC} (desenvolvimento rápido)"
echo -e "${BLUE}[INFO]${NC} 3. Acesse: ${GREEN}http://127.0.0.1:8000${NC}"
echo -e "${BLUE}[INFO]${NC} 4. (Opcional) Edite ${GREEN}.env${NC} para personalizar configurações"
echo ""
echo -e "${PURPLE}🔐 Credenciais padrão:${NC}"
echo -e "${BLUE}[INFO]${NC} Admin: ${GREEN}admin${NC} / ${GREEN}admin123${NC}"
echo -e "${BLUE}[INFO]${NC} Professor: ${GREEN}prof01${NC} / ${GREEN}senha123${NC}"
echo ""
echo -e "${PURPLE}🛠️  Scripts disponíveis:${NC}"
echo -e "${BLUE}[INFO]${NC} ${GREEN}./start.sh${NC}  - Inicialização completa com verificações"
echo -e "${BLUE}[INFO]${NC} ${GREEN}./dev.sh${NC}    - Desenvolvimento rápido (simples)"
echo -e "${BLUE}[INFO]${NC} ${GREEN}./reset.sh${NC}  - Reset completo do banco de dados"
echo -e "${BLUE}[INFO]${NC} ${GREEN}./setup.sh${NC}  - Este script de setup inicial"
echo ""