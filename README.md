# 🚗 Sistema de Agendamento de Veículos - UESPI

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2.7-green?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

Sistema completo para gerenciamento de agendamentos de veículos institucionais, desenvolvido para a Universidade Estadual do Piauí (UESPI).

[Características](#-características) •
[Pré-requisitos](#-pré-requisitos) •
[Instalação](#-instalação) •
[Uso](#-uso) •
[Documentação](#-documentação)

</div>

---

## 📋 Sobre o Projeto

O **Sistema de Agendamento de Veículos** é uma aplicação web desenvolvida em Django que permite o gerenciamento eficiente de veículos institucionais, possibilitando que professores agendem veículos para atividades acadêmicas, enquanto administradores controlam aprovações, disponibilidade e geram relatórios detalhados.

### 🎯 Funcionalidades Principais

#### Para Professores
- ✅ Cadastro e autenticação com email institucional (`@*.uespi.br` ou `@uespi.br`)
- 📅 Agendamento de veículos com seleção de data/hora
- 📊 Visualização de agendamentos em calendário
- 🔍 Acompanhamento de status (Pendente/Aprovado/Reprovado)
- 📱 Notificações por email sobre mudanças de status

#### Para Administradores
- 👥 Gestão completa de usuários
- 🚙 Cadastro e gerenciamento de veículos
- 📚 Gestão de cursos e limites de quilometragem
- ✔️ Aprovação/Reprovação de agendamentos
- 📈 Relatórios detalhados (geral, por curso, por professor)
- 📥 Exportação de dados em Excel e PDF
- 📊 Dashboard com estatísticas em tempo real

### 🏗️ Arquitetura do Sistema

```
agendamento_veiculos/
├── 🐳 Docker Configuration
│   ├── docker-compose.yml      # Orquestração de containers
│   └── Dockerfile              # Imagem da aplicação
│
├── 📦 Apps Django
│   ├── agendamentos/           # Gestão de agendamentos
│   │   ├── views/             # Views organizadas por funcionalidade
│   │   └── exports/           # Exportação Excel/PDF
│   ├── veiculos/              # Gestão de veículos
│   ├── cursos/                # Gestão de cursos
│   ├── usuarios/              # Autenticação customizada
│   └── dashboard/             # Dashboard e estatísticas
│
├── 🎨 Frontend
│   ├── templates/             # Templates HTML
│   └── static/                # CSS, JS, imagens
│
├── 🔧 Scripts
│   └── deploy-production.sh   # Script automatizado de deploy
│
└── ⚙️ Configurações
    ├── manage.py              # CLI do Django
    ├── requirements.txt       # Dependências Python
    └── .env                   # Variáveis de ambiente
```

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.12** - Linguagem de programação
- **Django 5.2.7** - Framework web
- **PostgreSQL 15** - Banco de dados relacional
- **Gunicorn** - Servidor WSGI para produção

### Frontend
- **HTML5/CSS3** - Estrutura e estilização
- **JavaScript** - Interatividade
- **Bootstrap** (implícito) - Framework CSS responsivo

### Bibliotecas Python
- **Pillow** - Processamento de imagens
- **openpyxl/xlsxwriter** - Exportação Excel
- **ReportLab** - Geração de PDFs
- **python-decouple** - Gerenciamento de configurações
- **whitenoise** - Servir arquivos estáticos

### DevOps
- **Docker & Docker Compose** - Containerização
- **GitHub Actions** (potencial) - CI/CD

---

## 📦 Pré-requisitos

### Para Desenvolvimento Local (sem Docker)
- Python 3.12+
- PostgreSQL 15+ ou SQLite3
- pip (gerenciador de pacotes Python)

### Para Produção com Docker (Recomendado)
- [Docker](https://docs.docker.com/get-docker/) 20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) 2.0+

---

## 🚀 Instalação

### 🐳 Opção 1: Docker (Recomendado para Produção)

#### 1. Clone o repositório
```bash
git clone https://github.com/HeitorLouzeiro/agendamento_veiculos.git
cd agendamento_veiculos
```

#### 2. Torne o script de deploy executável
```bash
chmod +x scripts/deploy-production.sh
```

#### 3. Execute o script de deploy completo
```bash
./scripts/deploy-production.sh
```

O script irá:
- ✅ Verificar instalação do Docker
- ✅ Criar arquivo `.env` com configurações padrão
- ✅ Construir imagens Docker
- ✅ Iniciar banco de dados PostgreSQL
- ✅ Executar migrações do banco
- ✅ Coletar arquivos estáticos
- ✅ Oferecer criação de superusuário
- ✅ Iniciar todos os serviços

#### 4. Acesse a aplicação
```
http://localhost:8000
```

### 💻 Opção 2: Desenvolvimento Local (sem Docker)

#### 1. Clone o repositório
```bash
git clone https://github.com/HeitorLouzeiro/agendamento_veiculos.git
cd agendamento_veiculos
```

#### 2. Crie e ative o ambiente virtual
```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### 3. Instale as dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env  # Se existir
# Ou crie manualmente o arquivo .env
```

Exemplo de `.env` para desenvolvimento:
```env
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
ALLOWED_HOSTS=localhost,127.0.0.1

# SQLite para desenvolvimento
DB_ENGINE=sqlite3

# Ou PostgreSQL
# DB_ENGINE=postgresql
# DB_NAME=agendamento_veiculos
# DB_USER=postgres
# DB_PASSWORD=postgres
# DB_HOST=localhost
# DB_PORT=5432

# Configurações regionais
LANGUAGE_CODE=pt-br
TIME_ZONE=America/Sao_Paulo

# Email (console para desenvolvimento)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@uespi.br
```

#### 5. Execute as migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Crie um superusuário
```bash
python manage.py createsuperuser
```

#### 7. Colete arquivos estáticos
```bash
python manage.py collectstatic --noinput
```

#### 8. Inicie o servidor de desenvolvimento
```bash
python manage.py runserver
```

#### 9. Acesse a aplicação
```
http://localhost:8000
```

---

## 📖 Uso

### 🐳 Comandos Docker

#### Modo Interativo (Menu)
```bash
./scripts/deploy-production.sh
```

Opções disponíveis:
1. **Deploy completo** - Configuração inicial completa
2. **Rebuild e restart** - Reconstruir e reiniciar serviços
3. **Executar migrações** - Aplicar migrações do banco
4. **Coletar arquivos estáticos** - Atualizar static files
5. **Criar superusuário** - Adicionar administrador
6. **Ver status** - Verificar containers em execução
7. **Ver logs** - Visualizar logs da aplicação
8. **Parar serviços** - Desligar todos os containers
9. **Sair** - Encerrar o menu

#### Modo Comando Direto
```bash
# Deploy completo
./scripts/deploy-production.sh deploy

# Reconstruir e reiniciar
./scripts/deploy-production.sh rebuild

# Executar migrações
./scripts/deploy-production.sh migrate

# Coletar arquivos estáticos
./scripts/deploy-production.sh static

# Criar superusuário
./scripts/deploy-production.sh superuser

# Ver status dos containers
./scripts/deploy-production.sh status

# Ver logs em tempo real
./scripts/deploy-production.sh logs

# Parar todos os serviços
./scripts/deploy-production.sh stop
```

#### Comandos Docker Compose Manuais

```bash
# Iniciar serviços em produção
docker-compose up -d

# Iniciar em modo desenvolvimento (com live reload)
docker-compose --profile dev up -d

# Ver logs
docker-compose logs -f web

# Parar serviços
docker-compose down

# Reconstruir imagens
docker-compose build --no-cache

# Executar comandos Django
docker-compose exec web python manage.py <comando>

# Acessar shell do Django
docker-compose exec web python manage.py shell

# Acessar bash do container
docker-compose exec web bash

# Backup do banco de dados
docker-compose exec db pg_dump -U postgres agendamento_veiculos > backup.sql

# Restaurar banco de dados
docker-compose exec -T db psql -U postgres agendamento_veiculos < backup.sql
```

### 💻 Comandos Desenvolvimento Local

```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Iniciar servidor de desenvolvimento
python manage.py runserver

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic

# Shell interativo do Django
python manage.py shell

# Verificar problemas no projeto
python manage.py check

# Limpar sessões expiradas
python manage.py clearsessions
```

---

## 📧 Configuração de Email

O sistema envia emails para ativação de conta e notificações. Veja [EMAIL_CONFIG.md](EMAIL_CONFIG.md) para instruções detalhadas.

### Desenvolvimento (Console)
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@uespi.br
```

### Produção (SMTP - Gmail)
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app-gmail
DEFAULT_FROM_EMAIL=noreply@uespi.br
```

> **Nota:** Para Gmail, gere uma "Senha de App" em: https://myaccount.google.com/apppasswords

---

## 🔐 Segurança

### Configurações de Produção

**IMPORTANTE:** Antes de fazer deploy em produção:

1. **Altere a SECRET_KEY** no arquivo `.env`:
```env
SECRET_KEY=gere-uma-chave-secreta-forte-e-unica-aqui
```

2. **Desative o DEBUG**:
```env
DEBUG=False
```

3. **Configure ALLOWED_HOSTS**:
```env
ALLOWED_HOSTS=seudominio.com,www.seudominio.com
```

4. **Use HTTPS** em produção (configure proxy reverso como Nginx)

5. **Configure backup automático** do banco de dados

### Gerando SECRET_KEY Segura

```python
# Execute no shell Python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## 📊 Estrutura do Banco de Dados

### Principais Models

#### **Usuario** (usuários/)
- Herda de `AbstractUser` do Django
- Campos: `username`, `email`, `tipo_usuario` (professor/administrador)
- Email institucional obrigatório: `@*.uespi.br`
- Ativação de conta via email

#### **Veiculo** (veiculos/)
- Campos: `placa`, `modelo`, `marca`, `ano`, `cor`, `capacidade_passageiros`
- UUID como primary key
- Status ativo/inativo

#### **Curso** (cursos/)
- Campos: `nome`, `limite_km_mensal`, `descricao`
- Controle de quilometragem mensal por curso

#### **Agendamento** (agendamentos/)
- Relacionamentos: `curso`, `professor`, `veiculo`
- Campos: `data_inicio`, `data_fim`, `status`, `km_previsto`
- Status: Pendente, Aprovado, Reprovado
- Validações de conflito de horários

---

## 📚 Documentação Adicional

### Documentos Principais
- **[📖 Índice Completo](docs/DOCUMENTATION_INDEX.md)** - Navegação em toda documentação
- **[⚡ Guia Rápido](docs/QUICKSTART.md)** - Início em 5 minutos
- **[📊 Visão Técnica](docs/PROJECT_OVERVIEW.md)** - Overview do projeto
- **[⌨️ Comandos](docs/COMMANDS.md)** - Referência de comandos
- **[🤝 Contribuindo](docs/CONTRIBUTING.md)** - Como contribuir
- **[👋 Boas-vindas](docs/WELCOME.md)** - Para novos usuários

### Configuração
- [EMAIL_CONFIG.md](EMAIL_CONFIG.md) - Configuração detalhada de email
- [LICENSE](LICENSE) - Licença do projeto

### Links Externos
- [Documentação Django](https://docs.djangoproject.com/)
- [Docker Docs](https://docs.docker.com/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

📖 **Leia o guia completo:** [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

### Padrões de Código
- Siga a PEP 8 para Python
- Use nomes descritivos para variáveis e funções
- Comente código complexo
- Escreva testes para novas funcionalidades

---

## 🐛 Solução de Problemas

### Erro: "Port 8000 already in use"
```bash
# Linux/Mac
sudo lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Erro: "Permission denied" ao executar script
```bash
chmod +x scripts/deploy-production.sh
```

### Erro de migração do banco
```bash
# Resetar migrações (CUIDADO: perda de dados)
docker-compose exec web python manage.py migrate --fake <app> zero
docker-compose exec web python manage.py migrate <app>
```

### Container não inicia
```bash
# Ver logs detalhados
docker-compose logs web
docker-compose logs db

# Rebuild completo
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## 📝 Changelog

### [1.0.0] - 2025-10-31
- ✨ Lançamento inicial do sistema
- 🚀 Suporte completo a Docker
- 📧 Sistema de ativação por email
- 📊 Dashboard com estatísticas
- 📥 Exportação Excel e PDF
- 🔐 Autenticação customizada

---

## 👨‍💻 Autor

**Heitor Louzeiro**

- GitHub: [@HeitorLouzeiro](https://github.com/HeitorLouzeiro)
- LinkedIn: [Heitor Louzeiro](https://www.linkedin.com/in/heitor-louzeiro)

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙏 Agradecimentos

- Universidade Estadual do Piauí (UESPI)
- Comunidade Django
- Todos os contribuidores

---

⭐ Se este projeto foi útil, considere dar uma estrela!

</div>
