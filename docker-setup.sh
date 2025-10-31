#!/bin/bash

# ========================================
# Script de Setup com Docker e PostgreSQL
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
echo "  🐳 SETUP DOCKER + POSTGRESQL"
echo "     Sistema de Agendamento Veículos"
echo "========================================="
echo -e "${NC}"

# Verificar Docker
echo -e "${BLUE}[INFO]${NC} Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERRO]${NC} Docker não encontrado!"
    echo -e "${YELLOW}[AVISO]${NC} Instale o Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}[SUCESSO]${NC} Docker encontrado: $(docker --version)"

# Verificar Docker Compose
echo -e "${BLUE}[INFO]${NC} Verificando Docker Compose..."
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}[ERRO]${NC} Docker Compose não encontrado!"
    echo -e "${YELLOW}[AVISO]${NC} Instale o Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}[SUCESSO]${NC} Docker Compose encontrado"

# Verificar se o Docker está rodando
echo -e "${BLUE}[INFO]${NC} Verificando se Docker está em execução..."
if ! docker info &> /dev/null; then
    echo -e "${RED}[ERRO]${NC} Docker não está em execução!"
    echo -e "${YELLOW}[AVISO]${NC} Inicie o serviço do Docker primeiro"
    exit 1
fi
echo -e "${GREEN}[SUCESSO]${NC} Docker está em execução"

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo -e "${BLUE}[INFO]${NC} Criando arquivo .env para Docker..."
    cat > .env << 'EOF'
# ========================================
# Variáveis de Ambiente - Docker/PostgreSQL
# Sistema de Agendamento de Veículos
# ========================================

# Segurança (OBRIGATÓRIO em produção)
SECRET_KEY=sua-chave-secreta-super-segura-aqui-mude-em-producao

# Modo de desenvolvimento
DEBUG=True

# Hosts permitidos (separados por vírgula)
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Configurações regionais
TIME_ZONE=America/Sao_Paulo
LANGUAGE_CODE=pt-br

# ========================================
# Configurações do PostgreSQL
# ========================================
DB_ENGINE=postgresql
DB_NAME=agendamento_veiculos
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=db
DB_PORT=5432
EOF
    echo -e "${GREEN}[SUCESSO]${NC} Arquivo .env criado com configurações do PostgreSQL!"
else
    echo -e "${YELLOW}[AVISO]${NC} Arquivo .env já existe"
    echo -e "${BLUE}[INFO]${NC} Verificando configurações do PostgreSQL..."
    
    # Verificar se tem as variáveis do PostgreSQL
    if ! grep -q "DB_ENGINE=postgresql" .env; then
        echo -e "${YELLOW}[AVISO]${NC} Adicionando configurações do PostgreSQL ao .env..."
        cat >> .env << 'EOF'

# ========================================
# Configurações do PostgreSQL
# ========================================
DB_ENGINE=postgresql
DB_NAME=agendamento_veiculos
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=db
DB_PORT=5432
EOF
        echo -e "${GREEN}[SUCESSO]${NC} Configurações do PostgreSQL adicionadas!"
    else
        echo -e "${GREEN}[SUCESSO]${NC} Configurações do PostgreSQL já existem no .env"
    fi
fi

# Parar containers existentes
echo -e "${BLUE}[INFO]${NC} Parando containers existentes (se houver)..."
docker compose down 2>/dev/null

# Limpar volumes antigos (opcional)
echo -e "${YELLOW}[AVISO]${NC} Deseja limpar os volumes do banco de dados? (s/N)"
read -r -n 1 limpar_volumes
echo ""
if [[ $limpar_volumes =~ ^[Ss]$ ]]; then
    echo -e "${BLUE}[INFO]${NC} Removendo volumes antigos..."
    docker compose down -v
    echo -e "${GREEN}[SUCESSO]${NC} Volumes removidos!"
fi

# Construir imagens
echo -e "${BLUE}[INFO]${NC} Construindo imagens Docker..."
docker compose build

# Iniciar o banco de dados primeiro
echo -e "${BLUE}[INFO]${NC} Iniciando container do PostgreSQL..."
docker compose up -d db

# Aguardar o PostgreSQL ficar pronto
echo -e "${BLUE}[INFO]${NC} Aguardando PostgreSQL ficar pronto..."
for i in {1..30}; do
    if docker compose exec -T db pg_isready -U postgres &> /dev/null; then
        echo -e "${GREEN}[SUCESSO]${NC} PostgreSQL está pronto!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Criar banco de dados (se não existir)
echo -e "${BLUE}[INFO]${NC} Verificando banco de dados..."
docker compose exec -T db psql -U postgres -lqt | cut -d \| -f 1 | grep -qw agendamento_veiculos
if [ $? -ne 0 ]; then
    echo -e "${BLUE}[INFO]${NC} Criando banco de dados..."
    docker compose exec -T db createdb -U postgres agendamento_veiculos
    echo -e "${GREEN}[SUCESSO]${NC} Banco de dados criado!"
else
    echo -e "${GREEN}[SUCESSO]${NC} Banco de dados já existe"
fi

# Executar makemigrations
echo -e "${BLUE}[INFO]${NC} Gerando migrações (makemigrations)..."
docker compose run --rm web python manage.py makemigrations

# Executar migrate
echo -e "${BLUE}[INFO]${NC} Aplicando migrações (migrate)..."
docker compose run --rm web python manage.py migrate

# Verificar se existem superusuários
echo -e "${BLUE}[INFO]${NC} Verificando usuários existentes..."
SUPERUSER_CHECK=$(docker compose run --rm web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if User.objects.filter(is_superuser=True).exists():
    print('SUPERUSER_EXISTS')
else:
    print('NO_SUPERUSER')
" 2>/dev/null)

if echo "$SUPERUSER_CHECK" | grep -q "NO_SUPERUSER"; then
    echo -e "${YELLOW}[AVISO]${NC} Nenhum superusuário encontrado."
    echo -e "${BLUE}[INFO]${NC} Carregando dados de exemplo..."
    docker compose run --rm web python manage.py load_sample_data
    echo -e "${GREEN}[SUCESSO]${NC} Dados de exemplo carregados!"
else
    echo -e "${GREEN}[SUCESSO]${NC} Superusuário já existe!"
fi

# Coletar arquivos estáticos
echo -e "${BLUE}[INFO]${NC} Coletando arquivos estáticos..."
docker compose run --rm web python manage.py collectstatic --noinput

# Tornar scripts executáveis
echo -e "${BLUE}[INFO]${NC} Configurando permissões dos scripts..."
chmod +x docker-start.sh docker-stop.sh docker-reset.sh 2>/dev/null

echo ""
echo -e "${GREEN}✅ SETUP DOCKER COMPLETO!${NC}"
echo ""
echo -e "${PURPLE}📋 Próximos passos:${NC}"
echo -e "${BLUE}[INFO]${NC} 1. Inicie os containers: ${GREEN}docker compose up -d${NC}"
echo -e "${BLUE}[INFO]${NC}    Ou use: ${GREEN}./docker-start.sh${NC}"
echo -e "${BLUE}[INFO]${NC} 2. Acesse: ${GREEN}http://localhost:8000${NC}"
echo -e "${BLUE}[INFO]${NC} 3. Para parar: ${GREEN}docker compose down${NC}"
echo -e "${BLUE}[INFO]${NC}    Ou use: ${GREEN}./docker-stop.sh${NC}"
echo ""
echo -e "${PURPLE}🔐 Credenciais padrão:${NC}"
echo -e "${BLUE}[INFO]${NC} Admin: ${GREEN}admin${NC} / ${GREEN}admin123${NC}"
echo -e "${BLUE}[INFO]${NC} Professor: ${GREEN}prof01${NC} / ${GREEN}senha123${NC}"
echo ""
echo -e "${PURPLE}🐳 Comandos úteis Docker:${NC}"
echo -e "${BLUE}[INFO]${NC} ${GREEN}docker compose up -d${NC}         - Iniciar containers"
echo -e "${BLUE}[INFO]${NC} ${GREEN}docker compose down${NC}          - Parar containers"
echo -e "${BLUE}[INFO]${NC} ${GREEN}docker compose logs -f${NC}       - Ver logs"
echo -e "${BLUE}[INFO]${NC} ${GREEN}docker compose ps${NC}            - Ver status dos containers"
echo -e "${BLUE}[INFO]${NC} ${GREEN}docker compose exec web bash${NC} - Acessar terminal do container"
echo ""
echo -e "${PURPLE}🗄️  PostgreSQL:${NC}"
echo -e "${BLUE}[INFO]${NC} Host: ${GREEN}localhost${NC}"
echo -e "${BLUE}[INFO]${NC} Porta: ${GREEN}5432${NC}"
echo -e "${BLUE}[INFO]${NC} Banco: ${GREEN}agendamento_veiculos${NC}"
echo -e "${BLUE}[INFO]${NC} Usuário: ${GREEN}postgres${NC}"
echo -e "${BLUE}[INFO]${NC} Senha: ${GREEN}postgres123${NC}"
echo ""