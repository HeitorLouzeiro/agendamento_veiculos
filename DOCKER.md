# Configuração do Docker para Agendamento de Veículos

## Requisitos

- Docker
- Docker Compose

## Configuração Inicial

### 1. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` conforme suas necessidades.

### 2. Executar setup automatizado

**Linux/Mac:**
```bash
chmod +x docker-setup.sh
./docker-setup.sh
```

**Windows:**
```cmd
docker-setup.bat
```

### 3. Configuração manual (alternativa)

```bash
# Construir as imagens
docker-compose build

# Iniciar o banco de dados
docker-compose up -d db

# Executar migrações
docker-compose run --rm web python manage.py migrate

# Criar superusuário
docker-compose run --rm web python manage.py createsuperuser
```

## Execução

### Modo Desenvolvimento (com live reload)
```bash
docker-compose --profile dev up
```

### Modo Produção
```bash
docker-compose up
```

### Executar em background
```bash
docker-compose up -d
```

## Comandos Úteis

### Parar os serviços
```bash
docker-compose down
```

### Visualizar logs
```bash
# Todos os serviços
docker-compose logs -f

# Apenas a aplicação web
docker-compose logs -f web

# Apenas o banco de dados
docker-compose logs -f db
```

### Executar comandos Django
```bash
# Migrações
docker-compose run --rm web python manage.py migrate

# Criar superusuário
docker-compose run --rm web python manage.py createsuperuser

# Coletar arquivos estáticos (apenas se necessário)
docker-compose run --rm web python manage.py collectstatic --noinput

# Shell Django
docker-compose run --rm web python manage.py shell

# Executar testes
docker-compose run --rm web python manage.py test

# Limpar containers e volumes (se houver problemas)
docker-compose down -v
docker-compose build --no-cache
```

### Backup e restore do banco de dados

**Backup:**
```bash
docker-compose exec db pg_dump -U postgres agendamento_veiculos > backup.sql
```

**Restore:**
```bash
docker-compose exec -T db psql -U postgres agendamento_veiculos < backup.sql
```

### Acessar o container
```bash
# Container da aplicação
docker-compose exec web bash

# Container do banco de dados
docker-compose exec db psql -U postgres -d agendamento_veiculos
```

## Estrutura dos Serviços

- **db**: PostgreSQL 15
- **web**: Aplicação Django (modo produção)
- **web-dev**: Aplicação Django (modo desenvolvimento)

## Portas

- Aplicação: http://localhost:8000
- PostgreSQL: localhost:5432

## Volumes

- `postgres_data`: Dados persistentes do PostgreSQL
- `static_volume`: Arquivos estáticos da aplicação

## Desenvolvimento Local (sem Docker)

Se preferir executar localmente sem Docker, configure no `.env`:

```env
DB_ENGINE=sqlite3
```

E execute normalmente:
```bash
python manage.py runserver
```