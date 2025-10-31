#!/bin/bash

# Script de Deploy para Produção - Sistema de Agendamento de Veículos
# Este script automatiza a configuração e deploy do ambiente de produção usando Docker

set -e  # Para a execução se houver erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_info() {
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

# Função para criar arquivo .env se não existir
create_env_file() {
    if [ -f .env ]; then
        print_warning "Arquivo .env já existe. Pulando criação..."
        return
    fi

    print_info "Criando arquivo .env para produção Docker com valores padrão..."

    # Cria o arquivo .env baseado no .env.example
    cat > .env << 'EOF'
# Configurações básicas da aplicação
DEBUG=False
SECRET_KEY=django-insecure-change-me-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Configurações do banco de dados
# Use 'sqlite3' para desenvolvimento local ou 'postgresql' para produção/Docker
DB_ENGINE=postgresql
DB_NAME=agendamento_veiculos
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Configurações de localização
LANGUAGE_CODE=pt-br
TIME_ZONE=America/Sao_Paulo

# Configurações de Email
# Para desenvolvimento - emails aparecem no console/terminal:
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Para produção - enviar emails reais via SMTP:
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=seu-email@gmail.com
# EMAIL_HOST_PASSWORD=sua-senha-de-app-do-gmail
# DEFAULT_FROM_EMAIL=noreply@uespi.br

# Observação: Para Gmail, use uma "Senha de App" (não a senha normal)
# Gere em: https://myaccount.google.com/apppasswords

# Configurações de arquivos estáticos (opcional)
STATIC_URL=/static/
STATIC_ROOT=/app/staticfiles/

# Configurações para Docker (opcional)
# Se você quiser personalizar as portas ou nomes dos containers
# COMPOSE_PROJECT_NAME=agendamento_veiculos
EOF

    print_success "Arquivo .env criado com sucesso!"
}

# Função para verificar se Docker está instalado
check_docker() {
    print_info "Verificando instalação do Docker..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker não está instalado. Por favor, instale o Docker primeiro."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
        exit 1
    fi
    
    print_success "Docker e Docker Compose encontrados!"
}

# Função para parar containers existentes
stop_containers() {
    print_info "Parando containers existentes..."
    docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true
    print_success "Containers parados!"
}

# Função para construir imagens Docker
build_images() {
    print_info "Construindo imagens Docker..."
    docker-compose build --no-cache || docker compose build --no-cache
    print_success "Imagens construídas com sucesso!"
}

# Função para iniciar o banco de dados
start_database() {
    print_info "Iniciando banco de dados PostgreSQL..."
    docker-compose up -d db || docker compose up -d db
    
    print_info "Aguardando banco de dados ficar pronto..."
    sleep 10
    
    # Verifica se o banco está acessível
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec -T db pg_isready -U ${DB_USER:-postgres} &> /dev/null || \
           docker compose exec -T db pg_isready -U ${DB_USER:-postgres} &> /dev/null; then
            print_success "Banco de dados está pronto!"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    print_error "Banco de dados não ficou pronto a tempo."
    exit 1
}

# Função para executar migrações
run_migrations() {
    print_info "Executando migrações do Django..."
    
    # Cria as migrações se necessário
    docker-compose run --rm web python manage.py makemigrations || \
    docker compose run --rm web python manage.py makemigrations
    
    # Aplica as migrações
    docker-compose run --rm web python manage.py migrate || \
    docker compose run --rm web python manage.py migrate
    
    print_success "Migrações executadas com sucesso!"
}

# Função para preparar arquivos estáticos
prepare_static_files() {
    print_info "Preparando arquivos estáticos..."
    
    # Corrige permissões do diretório static se necessário
    if [ -d "static" ] && [ ! -w "static" ]; then
        print_info "Corrigindo permissões do diretório static..."
        sudo chown -R $(whoami):$(whoami) static 2>/dev/null || true
    fi
    
    # Cria diretório de imagens se não existir
    mkdir -p static/images
    
    # Copia logo se existir em templates/images
    if [ -f "templates/images/logo.png" ]; then
        print_info "Copiando logo.png para static/images..."
        cp templates/images/logo.png static/images/
    fi
    
    print_success "Arquivos estáticos preparados!"
}

# Função para coletar arquivos estáticos
collect_static() {
    print_info "Coletando arquivos estáticos..."
    docker-compose run --rm web python manage.py collectstatic --noinput || \
    docker compose run --rm web python manage.py collectstatic --noinput
    print_success "Arquivos estáticos coletados!"
}

# Função para criar superusuário
create_superuser() {
    read -p "Deseja criar um superusuário? (s/N): " create_su
    if [[ $create_su =~ ^[Ss]$ ]]; then
        print_info "Criando superusuário..."
        docker-compose run --rm web python manage.py createsuperuser || \
        docker compose run --rm web python manage.py createsuperuser
    fi
}

# Função para iniciar todos os serviços
start_services() {
    print_info "Iniciando todos os serviços..."
    docker-compose up -d || docker compose up -d
    print_success "Serviços iniciados com sucesso!"
}

# Função para mostrar status dos containers
show_status() {
    print_info "Status dos containers:"
    docker-compose ps || docker compose ps
}

# Função para mostrar logs
show_logs() {
    print_info "Últimos logs do container web:"
    docker-compose logs --tail=50 web || docker compose logs --tail=50 web
}

# Menu principal
show_menu() {
    echo ""
    echo "=========================================="
    echo "  Deploy Produção - Agendamento Veículos"
    echo "=========================================="
    echo "1) Deploy completo (novo ambiente)"
    echo "2) Apenas rebuild e restart"
    echo "3) Executar migrações"
    echo "4) Coletar arquivos estáticos"
    echo "5) Criar superusuário"
    echo "6) Ver status dos containers"
    echo "7) Ver logs"
    echo "8) Parar todos os serviços"
    echo "9) Sair"
    echo "=========================================="
}

# Função de deploy completo
full_deploy() {
    print_info "Iniciando deploy completo..."
    
    check_docker
    create_env_file
    stop_containers
    build_images
    start_database
    run_migrations
    prepare_static_files
    collect_static
    create_superuser
    start_services
    show_status
    
    echo ""
    print_success "=========================================="
    print_success "  Deploy concluído com sucesso!"
    print_success "=========================================="
    print_info "Acesse a aplicação em: http://localhost:8000"
    print_info "Para ver os logs: docker-compose logs -f web"
    print_info "Para parar: docker-compose down"
}

# Função de rebuild e restart
rebuild_restart() {
    print_info "Reconstruindo e reiniciando serviços..."
    
    check_docker
    stop_containers
    build_images
    start_services
    show_status
    
    print_success "Serviços reconstruídos e reiniciados!"
}

# Script principal
main() {
    # Verifica se está no diretório correto
    if [ ! -f "manage.py" ]; then
        print_error "Este script deve ser executado a partir do diretório raiz do projeto!"
        exit 1
    fi

    # Se não houver argumentos, mostra o menu
    if [ $# -eq 0 ]; then
        while true; do
            show_menu
            read -p "Escolha uma opção: " choice
            
            case $choice in
                1)
                    full_deploy
                    ;;
                2)
                    rebuild_restart
                    ;;
                3)
                    check_docker
                    run_migrations
                    ;;
                4)
                    check_docker
                    prepare_static_files
                    collect_static
                    ;;
                5)
                    check_docker
                    create_superuser
                    ;;
                6)
                    check_docker
                    show_status
                    ;;
                7)
                    check_docker
                    show_logs
                    read -p "Pressione ENTER para continuar..."
                    ;;
                8)
                    check_docker
                    stop_containers
                    ;;
                9)
                    print_info "Saindo..."
                    exit 0
                    ;;
                *)
                    print_error "Opção inválida!"
                    ;;
            esac
        done
    else
        # Processa argumentos de linha de comando
        case $1 in
            deploy)
                full_deploy
                ;;
            rebuild)
                rebuild_restart
                ;;
            migrate)
                check_docker
                run_migrations
                ;;
            static)
                check_docker
                prepare_static_files
                collect_static
                ;;
            superuser)
                check_docker
                create_superuser
                ;;
            status)
                check_docker
                show_status
                ;;
            logs)
                check_docker
                docker-compose logs -f web || docker compose logs -f web
                ;;
            stop)
                check_docker
                stop_containers
                ;;
            *)
                echo "Uso: $0 [deploy|rebuild|migrate|static|superuser|status|logs|stop]"
                echo ""
                echo "Ou execute sem argumentos para modo interativo."
                exit 1
                ;;
        esac
    fi
}

# Executa o script principal
main "$@"
