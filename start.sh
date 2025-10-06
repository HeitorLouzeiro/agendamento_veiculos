#!/bin/bash

# ========================================
# Script de Inicialização Rápida
# Sistema de Agendamento de Veículos
# ========================================

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}"
    echo "========================================="
    echo "  🚗 SISTEMA DE AGENDAMENTO VEÍCULOS"
    echo "     Inicialização Rápida"
    echo "========================================="
    echo -e "${NC}"
}

# Função para verificar se está no diretório correto
check_directory() {
    if [ ! -f "manage.py" ]; then
        print_error "manage.py não encontrado! Execute este script na raiz do projeto Django."
        exit 1
    fi
}

# Função para ativar ambiente virtual
activate_venv() {
    if [ -d "venv" ]; then
        print_status "Ativando ambiente virtual..."
        source venv/bin/activate
        print_success "Ambiente virtual ativado!"
    else
        print_warning "Ambiente virtual não encontrado. Criando novo ambiente..."
        python3 -m venv venv
        source venv/bin/activate
        print_success "Ambiente virtual criado e ativado!"
        
        print_status "Instalando dependências..."
        pip install -r requirements.txt
        print_success "Dependências instaladas!"
    fi
}

# Função para executar migrações
run_migrations() {
    print_status "Verificando migrações..."
    python manage.py makemigrations --check --dry-run > /dev/null 2>&1
    
    if [ $? -ne 0 ]; then
        print_status "Criando migrações..."
        python manage.py makemigrations
    fi
    
    print_status "Aplicando migrações..."
    python manage.py migrate
    print_success "Migrações aplicadas!"
}

# Função para verificar superusuário
check_superuser() {
    print_status "Verificando se existe superusuário..."
    python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('exists' if User.objects.filter(is_superuser=True).exists() else 'none')" > /tmp/superuser_check 2>/dev/null
    
    if grep -q "none" /tmp/superuser_check; then
        print_warning "Nenhum superusuário encontrado!"
        echo -e "${YELLOW}Deseja carregar dados de exemplo (inclui administradores)? [y/N]${NC}"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            load_sample_data
        else
            print_status "Execute 'python manage.py createsuperuser' para criar um administrador."
        fi
    else
        print_success "Superusuário encontrado!"
    fi
    
    rm -f /tmp/superuser_check
}

# Função para carregar dados de exemplo
load_sample_data() {
    print_status "Carregando dados de exemplo..."
    python manage.py load_sample_data --administradores 3 --professores 5 --agendamentos 15
    print_success "Dados de exemplo carregados!"
}

# Função para verificar porta
check_port() {
    PORT=${1:-8000}
    if netstat -tuln | grep -q ":$PORT "; then
        print_warning "Porta $PORT já está em uso!"
        print_status "Tentando porta alternativa..."
        for port in 8001 8002 8003 8004 8005; do
            if ! netstat -tuln | grep -q ":$port "; then
                PORT=$port
                print_success "Usando porta $PORT"
                break
            fi
        done
    fi
    echo $PORT
}

# Função principal de inicialização
start_server() {
    print_header
    
    # Verificações iniciais
    check_directory
    activate_venv
    run_migrations
    check_superuser
    
    # Determinar porta
    PORT=$(check_port 8000)
    
    print_success "🚀 Iniciando servidor Django..."
    print_status "Acesse: ${GREEN}http://127.0.0.1:$PORT${NC}"
    print_status "Admin: ${GREEN}http://127.0.0.1:$PORT/admin${NC}"
    print_status "Para parar o servidor: ${YELLOW}Ctrl+C${NC}"
    
    echo ""
    echo -e "${PURPLE}=========================================${NC}"
    
    # Iniciar servidor
    python manage.py runserver $PORT
}

# Função para mostrar ajuda
show_help() {
    echo "Uso: $0 [OPÇÃO]"
    echo ""
    echo "Opções:"
    echo "  start, -s, --start     Inicia o servidor (padrão)"
    echo "  data, -d, --data       Apenas carrega dados de exemplo"
    echo "  setup, --setup         Apenas configuração inicial"
    echo "  help, -h, --help       Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0                     # Inicia o servidor"
    echo "  $0 start              # Inicia o servidor"
    echo "  $0 data               # Carrega apenas dados"
    echo "  $0 setup              # Apenas configuração"
}

# Função para configuração inicial apenas
setup_only() {
    print_header
    check_directory
    activate_venv
    run_migrations
    check_superuser
    print_success "✅ Configuração inicial concluída!"
    print_status "Execute '$0 start' para iniciar o servidor."
}

# Função para carregar apenas dados
data_only() {
    print_header
    check_directory
    activate_venv
    load_sample_data
    print_success "✅ Dados carregados!"
}

# Processar argumentos
case "${1:-start}" in
    start|-s|--start)
        start_server
        ;;
    data|-d|--data)
        data_only
        ;;
    setup|--setup)
        setup_only
        ;;
    help|-h|--help)
        show_help
        ;;
    *)
        print_error "Opção inválida: $1"
        show_help
        exit 1
        ;;
esac