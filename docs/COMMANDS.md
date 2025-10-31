# 📝 Comandos Úteis - Sistema de Agendamento de Veículos

Este arquivo contém uma referência rápida dos comandos mais utilizados no projeto.

---

## 🐳 Comandos Docker

### Gerenciamento de Containers

```bash
# Iniciar todos os serviços
docker-compose up -d

# Iniciar com logs em tempo real
docker-compose up

# Parar todos os serviços
docker-compose down

# Parar e remover volumes (CUIDADO: apaga o banco de dados)
docker-compose down -v

# Reiniciar todos os serviços
docker-compose restart

# Reiniciar apenas o serviço web
docker-compose restart web

# Ver status dos containers
docker-compose ps

# Ver logs
docker-compose logs

# Ver logs em tempo real
docker-compose logs -f

# Ver logs apenas do serviço web
docker-compose logs -f web

# Ver últimas 50 linhas de log
docker-compose logs --tail=50 web
```

### Build e Rebuild

```bash
# Construir imagens
docker-compose build

# Construir sem usar cache
docker-compose build --no-cache

# Rebuild completo (parar, rebuild, iniciar)
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Modo Desenvolvimento

```bash
# Iniciar em modo desenvolvimento (com live reload)
docker-compose --profile dev up -d

# Ver logs do modo desenvolvimento
docker-compose logs -f web-dev
```

---

## 🔧 Comandos Django via Docker

### Migrações

```bash
# Criar migrações
docker-compose exec web python manage.py makemigrations

# Aplicar migrações
docker-compose exec web python manage.py migrate

# Ver status das migrações
docker-compose exec web python manage.py showmigrations

# Reverter migração específica
docker-compose exec web python manage.py migrate <app_name> <migration_name>

# Reverter todas as migrações de um app
docker-compose exec web python manage.py migrate <app_name> zero
```

### Usuários e Permissões

```bash
# Criar superusuário
docker-compose exec web python manage.py createsuperuser

# Alterar senha de usuário
docker-compose exec web python manage.py changepassword <username>

# Criar usuário via shell
docker-compose exec web python manage.py shell
>>> from usuarios.models import Usuario
>>> user = Usuario.objects.create_user('nome', 'email@uespi.br', 'senha')
>>> user.tipo_usuario = 'administrador'
>>> user.save()
```

### Arquivos Estáticos

```bash
# Coletar arquivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Limpar arquivos estáticos
docker-compose exec web python manage.py collectstatic --clear --noinput
```

### Shell e Inspeção

```bash
# Acessar shell do Django
docker-compose exec web python manage.py shell

# Acessar shell bash do container
docker-compose exec web bash

# Acessar shell do PostgreSQL
docker-compose exec db psql -U postgres -d agendamento_veiculos

# Ver configurações do Django
docker-compose exec web python manage.py diffsettings
```

### Dados e Fixtures

```bash
# Exportar dados (criar fixture)
docker-compose exec web python manage.py dumpdata > fixture.json

# Exportar dados de um app específico
docker-compose exec web python manage.py dumpdata agendamentos > agendamentos.json

# Importar dados
docker-compose exec web python manage.py loaddata fixture.json

# Limpar sessões expiradas
docker-compose exec web python manage.py clearsessions
```

---

## 🗄️ Comandos do Banco de Dados

### Backup

```bash
# Backup completo do banco
docker-compose exec db pg_dump -U postgres agendamento_veiculos > backup.sql

# Backup com timestamp
docker-compose exec db pg_dump -U postgres agendamento_veiculos > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup apenas da estrutura (schema)
docker-compose exec db pg_dump -U postgres --schema-only agendamento_veiculos > schema.sql

# Backup apenas dos dados
docker-compose exec db pg_dump -U postgres --data-only agendamento_veiculos > data.sql
```

### Restauração

```bash
# Restaurar banco de dados
docker-compose exec -T db psql -U postgres agendamento_veiculos < backup.sql

# Restaurar recriando o banco
docker-compose exec db dropdb -U postgres agendamento_veiculos
docker-compose exec db createdb -U postgres agendamento_veiculos
docker-compose exec -T db psql -U postgres agendamento_veiculos < backup.sql
```

### Consultas Úteis

```bash
# Listar todos os bancos
docker-compose exec db psql -U postgres -c "\l"

# Listar tabelas
docker-compose exec db psql -U postgres -d agendamento_veiculos -c "\dt"

# Ver tamanho do banco
docker-compose exec db psql -U postgres -c "SELECT pg_database_size('agendamento_veiculos');"

# Contar registros
docker-compose exec db psql -U postgres -d agendamento_veiculos -c "SELECT COUNT(*) FROM agendamentos_agendamento;"
```

---

## 📜 Script de Deploy

### Modo Interativo (Menu)

```bash
./scripts/deploy-production.sh
```

### Comandos Diretos

```bash
# Deploy completo (primeira vez)
./scripts/deploy-production.sh deploy

# Rebuild e restart
./scripts/deploy-production.sh rebuild

# Executar migrações
./scripts/deploy-production.sh migrate

# Coletar arquivos estáticos
./scripts/deploy-production.sh static

# Criar superusuário
./scripts/deploy-production.sh superuser

# Ver status
./scripts/deploy-production.sh status

# Ver logs
./scripts/deploy-production.sh logs

# Parar serviços
./scripts/deploy-production.sh stop
```

### Tornar o Script Executável

```bash
# Dar permissão de execução
chmod +x scripts/deploy-production.sh

# Verificar permissões
ls -la scripts/deploy-production.sh
```

---

## 💻 Comandos para Desenvolvimento Local (sem Docker)

### Ambiente Virtual

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual (Linux/Mac)
source venv/bin/activate

# Ativar ambiente virtual (Windows)
venv\Scripts\activate

# Desativar ambiente virtual
deactivate

# Instalar dependências
pip install -r requirements.txt

# Atualizar pip
pip install --upgrade pip
```

### Django

```bash
# Iniciar servidor de desenvolvimento
python manage.py runserver

# Iniciar em porta diferente
python manage.py runserver 8080

# Iniciar permitindo acesso externo
python manage.py runserver 0.0.0.0:8000

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic

# Shell do Django
python manage.py shell

# Verificar problemas
python manage.py check

# Limpar sessões
python manage.py clearsessions
```

---

## 🔍 Comandos de Depuração

### Logs e Informações

```bash
# Ver logs em tempo real com filtro
docker-compose logs -f web | grep ERROR

# Ver uso de recursos dos containers
docker stats

# Inspecionar container
docker inspect agendamento_veiculos_web_1

# Ver variáveis de ambiente do container
docker-compose exec web env

# Ver processos rodando no container
docker-compose exec web ps aux
```

### Limpeza

```bash
# Remover containers parados
docker container prune

# Remover imagens não utilizadas
docker image prune

# Remover volumes não utilizados
docker volume prune

# Limpeza completa (CUIDADO!)
docker system prune -a --volumes
```

---

## 📊 Comandos de Monitoramento

### Performance

```bash
# Ver uso de CPU e memória
docker stats

# Ver espaço em disco dos volumes
docker system df

# Ver logs de acesso (últimos 100)
docker-compose exec web tail -100 /var/log/gunicorn/access.log

# Monitorar conexões do PostgreSQL
docker-compose exec db psql -U postgres -c "SELECT * FROM pg_stat_activity;"
```

### Saúde do Sistema

```bash
# Verificar se o banco está pronto
docker-compose exec db pg_isready -U postgres

# Testar conexão HTTP
curl http://localhost:8000

# Ver versão do Python
docker-compose exec web python --version

# Ver versão do Django
docker-compose exec web python manage.py version

# Ver pacotes instalados
docker-compose exec web pip list
```

---

## 🔐 Comandos de Segurança

### Gerar Chaves

```bash
# Gerar SECRET_KEY do Django
docker-compose exec web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Ou localmente
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Permissões

```bash
# Corrigir permissões de arquivos
sudo chown -R $(whoami):$(whoami) .

# Corrigir permissões de diretórios
find . -type d -exec chmod 755 {} \;

# Corrigir permissões de arquivos
find . -type f -exec chmod 644 {} \;

# Tornar scripts executáveis
chmod +x scripts/*.sh
```

---

## 📦 Comandos Git

### Básicos

```bash
# Clonar repositório
git clone https://github.com/HeitorLouzeiro/agendamento_veiculos.git

# Ver status
git status

# Adicionar arquivos
git add .

# Commit
git commit -m "Mensagem do commit"

# Push
git push origin main

# Pull
git pull origin main
```

### Branches

```bash
# Criar e mudar para nova branch
git checkout -b feature/nova-funcionalidade

# Listar branches
git branch -a

# Mudar de branch
git checkout main

# Deletar branch local
git branch -d feature/antiga
```

---

## 🎯 Atalhos Úteis

### Aliases para .bashrc ou .zshrc

```bash
# Adicione ao seu arquivo ~/.bashrc ou ~/.zshrc

# Docker Compose
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dcr='docker-compose restart'

# Django via Docker
alias dj='docker-compose exec web python manage.py'
alias djmm='docker-compose exec web python manage.py makemigrations'
alias djm='docker-compose exec web python manage.py migrate'
alias djr='docker-compose exec web python manage.py runserver'
alias djs='docker-compose exec web python manage.py shell'

# Deploy
alias deploy='./scripts/deploy-production.sh'
```

Após adicionar, execute:
```bash
source ~/.bashrc  # ou ~/.zshrc
```

---

## 📌 Comandos para Memorizar

| Comando | Descrição |
|---------|-----------|
| `chmod +x scripts/deploy-production.sh` | Tornar script executável |
| `./scripts/deploy-production.sh deploy` | Deploy completo |
| `docker-compose up -d` | Iniciar sistema |
| `docker-compose down` | Parar sistema |
| `docker-compose logs -f web` | Ver logs em tempo real |
| `docker-compose exec web python manage.py migrate` | Aplicar migrações |
| `docker-compose exec web bash` | Acessar terminal do container |
| `http://localhost:8000` | URL da aplicação |

---

<div align="center">

**Referência Rápida de Comandos**

Para mais informações, consulte o [README.md](README.md) completo.

</div>
