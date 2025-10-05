# 🚗 Sistema de Agendamento de Veículos

Sistema completo de gerenciamento de agendamentos de veículos desenvolvido com **Django 5.2** e **Python 3.12**, com controle de quilometragem, trajetos e sistema de aprovação.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)

## 📋 Sumário

- [🚀 Início Rápido](#-início-rápido)
- [🏗️ Arquitetura](#%EF%B8%8F-arquitetura)
- [✨ Funcionalidades](#-funcionalidades)
- [🛠️ Tecnologias](#%EF%B8%8F-tecnologias)
- [📦 Instalação](#-instalação)
- [🔧 Configuração](#-configuração)
- [🏃‍♂️ Como Executar](#%EF%B8%8F-como-executar)
- [📖 Uso do Sistema](#-uso-do-sistema)
- [🔒 Autenticação](#-autenticação)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🗄️ Modelos de Dados](#%EF%B8%8F-modelos-de-dados)
- [👥 Colaboradores](#-colaboradores)
- [🤝 Contribuição](#-contribuição)
- [📜 Licença](#-licença)

## 🚀 Início Rápido

```bash
# Clone o repositório
git clone https://github.com/HeitorLouzeiro/agendamento_veiculos.git
cd agendamento_veiculos

# Crie e ative o ambiente virtual (Windows)
python -m venv venv
venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Execute as migrações
python manage.py migrate

# Crie um superusuário
python manage.py createsuperuser

# (Opcional) Carregue dados de exemplo
python load_sample_data.py

# Inicie o servidor
python manage.py runserver
```

Acesse: **http://127.0.0.1:8000**

## 🏗️ Arquitetura

O sistema segue a arquitetura **MVT (Model-View-Template)** do Django:

```
┌─────────────────────────────────────────────────────────────┐
│                    Cliente (Browser)                        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Request/Response
┌────────────────────────▼────────────────────────────────────┐
│                    Django Framework                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   URLs       │─►│    Views     │◄►│   Templates  │     │
│  │  (Routers)   │  │ (Controllers)│  │    (HTML)    │     │
│  └──────────────┘  └──────┬───────┘  └──────────────┘     │
│                            │                                 │
│                    ┌───────▼────────┐                       │
│                    │     Models     │                       │
│                    │  (ORM Layer)   │                       │
│                    └───────┬────────┘                       │
└────────────────────────────┼────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  SQLite Database │
                    └─────────────────┘
```

### Aplicações Django

- **usuarios** - Autenticação e gestão de usuários
- **cursos** - Cadastro e controle de cursos
- **veiculos** - Gestão de veículos
- **agendamentos** - Controle de agendamentos e trajetos
- **dashboard** - Painel principal do sistema

## ✨ Funcionalidades

### 👨‍🏫 Para Professores
- ✅ Criar solicitações de agendamento de veículos
- ✅ Visualizar histórico de agendamentos próprios
- ✅ Registrar trajetos realizados com quilometragem
- ✅ Editar perfil e alterar senha
- ✅ Recuperação de senha por perguntas de segurança
- ✅ Acompanhar status das solicitações

### 👔 Para Administradores
- ✅ Aprovar ou reprovar solicitações de agendamento
- ✅ Gerenciar cadastro de veículos (CRUD completo)
- ✅ Gerenciar cadastro de cursos (CRUD completo)
- ✅ Gerenciar usuários (professores e administradores)
- ✅ Visualizar todos os agendamentos do sistema
- ✅ Monitorar uso de quilometragem por curso
- ✅ Dashboard com estatísticas e visão geral
- ✅ Controle de limite de KM mensal por curso

### 🔧 Funcionalidades do Sistema
- ✅ Sistema de autenticação por e-mail ou username
- ✅ Validação automática de conflitos de horários
- ✅ Controle de limite de KM mensal por curso
- ✅ Histórico completo de trajetos e quilometragem
- ✅ Interface responsiva para desktop e mobile
- ✅ Notificações de status de agendamento
- ✅ Relatórios de uso de veículos
- ✅ Sistema de busca e filtros avançados

## 🛠️ Tecnologias

### Backend
- **Python** 3.12+ - Linguagem de programação
- **Django** 5.2.7 - Framework web
- **SQLite** - Banco de dados (desenvolvimento)
- **Django ORM** - Mapeamento objeto-relacional
- **Django Auth** - Sistema de autenticação

### Frontend
- **HTML5/CSS3** - Estrutura e estilo
- **JavaScript** - Interatividade no cliente
- **Bootstrap** 5 - Framework CSS responsivo
- **jQuery** - Biblioteca JavaScript

### Bibliotecas e Dependências
- **django-debug-toolbar** 6.0.0 - Ferramenta de debug
- **Pillow** 11.3.0 - Processamento de imagens
- **python-decouple** 3.8 - Gerenciamento de variáveis de ambiente
- **python-dotenv** 1.1.1 - Carregamento de variáveis .env
- **Faker** 37.8.0 - Geração de dados de teste
- **pytz** 2025.2 - Suporte a fusos horários
- **gunicorn** 23.0.0 - Servidor WSGI para produção
- **whitenoise** 6.11.0 - Servir arquivos estáticos em produção

## 📦 Instalação

### Pré-requisitos

- **Python** 3.12 ou superior
- **pip** (gerenciador de pacotes Python)
- **Git** (para clonar o repositório)
- **Virtualenv** (recomendado)

### Verificação de Dependências

```bash
# Verificar Python
python --version

# Verificar pip
pip --version

# Verificar Git
git --version
```

### Instalação Completa

#### 1. Clone o repositório

```bash
git clone https://github.com/HeitorLouzeiro/agendamento_veiculos.git
cd agendamento_veiculos
```

#### 2. Crie e ative o ambiente virtual

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

#### 4. Execute as migrações do banco de dados

```bash
python manage.py migrate
```

#### 5. Crie um superusuário (administrador)

```bash
python manage.py createsuperuser
```

Siga as instruções para criar o primeiro administrador do sistema.

#### 6. (Opcional) Carregue dados de exemplo

```bash
python load_sample_data.py
```

Este script criará automaticamente:
- 🔐 **3 administradores** com credenciais de teste
- 👨‍🏫 **10 professores** com perfis completos
- 📚 **5 cursos** diversos com limites de KM
- 🚗 **8 veículos** com diferentes características
- 📅 **30 agendamentos** com status variados
- 🗺️ **Trajetos** associados aos agendamentos aprovados

#### 7. Inicie o servidor de desenvolvimento

```bash
python manage.py runserver
```

✅ **Sistema pronto!** Acesse: http://127.0.0.1:8000

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (opcional para desenvolvimento):

```env
# Segurança
SECRET_KEY=sua-chave-secreta-super-segura-aqui-123456789
DEBUG=True

# Hosts permitidos
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de dados
DATABASE_URL=sqlite:///db.sqlite3

# Fuso horário
TIME_ZONE=America/Sao_Paulo
LANGUAGE_CODE=pt-br
```

### Configurações Importantes

#### Desenvolvimento
```python
DEBUG = True
ALLOWED_HOSTS = []
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### Produção

Para ambiente de produção, certifique-se de:

1. ⚠️ Definir `DEBUG = False`
2. 🌐 Configurar `ALLOWED_HOSTS` com os domínios permitidos
3. 🔑 Usar uma `SECRET_KEY` segura e única
4. 💾 Configurar banco de dados PostgreSQL ou MySQL
5. 📦 Coletar arquivos estáticos:
   ```bash
   python manage.py collectstatic --noinput
   ```
6. 🚀 Usar servidor WSGI (Gunicorn):
   ```bash
   gunicorn agendamento_veiculos.wsgi:application
   ```

### Estrutura de Configuração

| Configuração | Desenvolvimento | Produção |
|--------------|----------------|----------|
| **DEBUG** | True | False |
| **Banco de Dados** | SQLite | PostgreSQL/MySQL |
| **Servidor** | runserver | Gunicorn + Nginx |
| **ALLOWED_HOSTS** | [] | ['seu-dominio.com'] |
| **STATIC_ROOT** | - | /var/www/static/ |

## 🏃‍♂️ Como Executar

### Desenvolvimento Local

```bash
# Ativar ambiente virtual (Windows CMD)
venv\Scripts\activate

# Executar servidor de desenvolvimento
python manage.py runserver

# Servidor em porta customizada
python manage.py runserver 8080

# Acessível na rede local
python manage.py runserver 0.0.0.0:8000
```

### Comandos Úteis

```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic

# Shell interativo Django
python manage.py shell

# Carregar dados de exemplo
python load_sample_data.py
```

## 📖 Uso do Sistema

### Acessos

- 🌐 **Sistema Principal**: http://127.0.0.1:8000
- 🔐 **Login**: http://127.0.0.1:8000/login/
- 📊 **Dashboard**: http://127.0.0.1:8000/dashboard/
- ⚙️ **Admin Django**: http://127.0.0.1:8000/admin/

### Credenciais Padrão

Após executar `python load_sample_data.py`:

```
👤 Administrador 1
Username: admin
Senha: admin123
Email: admin@example.com

👤 Administrador 2
Username: admin2
Senha: admin123
Email: admin2@example.com

👤 Professor
Username: professor1
Senha: prof123
Email: professor1@example.com
```

### Fluxo de Trabalho

#### 👨‍🏫 Para Professores:

1. 🔐 **Login** no sistema
2. 📅 Acesse **"Agendamentos"** > **"Novo Agendamento"**
3. 📝 Preencha os dados:
   - Curso
   - Veículo
   - Data/hora de início
   - Data/hora de fim
4. ⏳ Aguarde a **aprovação** do administrador
5. ✅ Após aprovação, **registre os trajetos** realizados com quilometragem

#### 👔 Para Administradores:

1. 🔐 **Login** no sistema
2. 📋 Acesse **"Agendamentos"** para ver todas as solicitações
3. ✅ Clique em **"Aprovar"** ou ❌ **"Reprovar"** nas solicitações pendentes
4. 🚗 Gerencie **veículos** (adicionar, editar, inativar)
5. 📚 Gerencie **cursos** (adicionar, editar, configurar limites de KM)
6. 👥 Gerencie **usuários** (professores e administradores)
7. 📊 Monitore o **uso de quilometragem** por curso no dashboard

### Interface Admin Django

Acesse `/admin/` para usar a interface administrativa completa do Django com recursos avançados:
- Gestão completa de todos os modelos
- Filtros e buscas avançadas
- Edição em massa
- Histórico de alterações

## � Autenticação

O sistema utiliza o sistema de autenticação nativo do Django com melhorias:

### Níveis de Acesso

| Tipo | Permissões |
|------|-----------|
| **Administrador** | Acesso total ao sistema, incluindo gestão de usuários, aprovação de agendamentos e configurações |
| **Professor** | Criar agendamentos, registrar trajetos e visualizar apenas seus próprios agendamentos |

### Proteção de Rotas

- **Públicas**: Login, recuperação de senha
- **Protegidas (Login Required)**: Dashboard, agendamentos, perfil
- **Admin Only**: Gestão de usuários, aprovação de agendamentos, CRUD de veículos e cursos

### Sistema de Login

- ✅ Autenticação por **e-mail** ou **username**
- ✅ Backend customizado (`EmailOrUsernameBackend`)
- ✅ Sessões seguras com Django
- ✅ Recuperação de senha por **perguntas de segurança**
- ✅ Proteção CSRF em formulários
- ✅ Validação de senhas fortes

## �📁 Estrutura do Projeto

```
agendamento_veiculos/
├── 📁 agendamento_veiculos/      # Configurações do projeto Django
│   ├── 📄 __init__.py
│   ├── 📄 settings.py            # Configurações principais
│   ├── 📄 urls.py                # URLs raiz do projeto
│   ├── 📄 wsgi.py                # Configuração WSGI
│   └── 📄 asgi.py                # Configuração ASGI
│
├── 📁 usuarios/                  # App de usuários
│   ├── 📄 models.py              # Model Usuario (AbstractUser customizado)
│   ├── 📄 views.py               # Views de autenticação e perfil
│   ├── 📄 forms.py               # Formulários de usuário
│   ├── 📄 backends.py            # Backend de autenticação customizado
│   ├── 📄 urls.py                # URLs do app
│   ├── 📄 admin.py               # Configuração do admin
│   └── 📁 migrations/            # Migrações do banco
│
├── 📁 cursos/                    # App de cursos
│   ├── 📄 models.py              # Model Curso
│   ├── 📄 views.py               # CRUD de cursos
│   ├── 📄 forms.py               # Formulários de curso
│   ├── 📄 urls.py                # URLs do app
│   ├── 📄 admin.py               # Configuração do admin
│   └── 📁 migrations/            # Migrações do banco
│
├── 📁 veiculos/                  # App de veículos
│   ├── 📄 models.py              # Model Veiculo
│   ├── 📄 views.py               # CRUD de veículos
│   ├── 📄 forms.py               # Formulários de veículo
│   ├── 📄 urls.py                # URLs do app
│   ├── 📄 admin.py               # Configuração do admin
│   └── 📁 migrations/            # Migrações do banco
│
├── 📁 agendamentos/              # App de agendamentos
│   ├── 📄 models.py              # Models: Agendamento, Trajeto
│   ├── 📄 views.py               # Views de agendamento e trajeto
│   ├── 📄 forms.py               # Formulários de agendamento
│   ├── 📄 urls.py                # URLs do app
│   ├── 📄 admin.py               # Configuração do admin
│   └── 📁 migrations/            # Migrações do banco
│
├── 📁 dashboard/                 # App do dashboard
│   ├── 📄 models.py              # (sem models específicos)
│   ├── 📄 views.py               # View do dashboard principal
│   ├── 📄 urls.py                # URLs do app
│   └── 📁 migrations/            # Migrações do banco
│
├── 📁 templates/                 # Templates HTML
│   ├── 📄 base.html              # Template base
│   ├── 📁 usuarios/              # Templates de autenticação
│   │   ├── 📄 login.html
│   │   ├── 📄 registro.html
│   │   ├── 📄 editar_perfil.html
│   │   └── 📄 alterar_senha.html
│   ├── 📁 cursos/                # Templates de cursos
│   │   ├── 📄 lista.html
│   │   ├── 📄 form.html
│   │   └── 📄 deletar.html
│   ├── 📁 veiculos/              # Templates de veículos
│   │   ├── 📄 lista.html
│   │   ├── 📄 form.html
│   │   └── 📄 deletar.html
│   ├── 📁 agendamentos/          # Templates de agendamentos
│   │   ├── 📄 lista.html
│   │   ├── 📄 form.html
│   │   ├── 📄 detalhe.html
│   │   ├── 📄 aprovacao.html
│   │   └── 📄 reprovar.html
│   └── 📁 dashboard/             # Templates do dashboard
│       └── 📄 index.html
│
├── 📄 manage.py                  # Script de gerenciamento Django
├── 📄 requirements.txt           # Dependências do projeto
├── 📄 load_sample_data.py        # Script para dados de exemplo
├── 📄 db.sqlite3                 # Banco de dados SQLite
└── 📄 README.md                  # Este arquivo
```

## 🗄️ Modelos de Dados

### 👤 Usuario (AbstractUser customizado)

```python
class Usuario(AbstractUser):
    tipo_usuario        # 'professor' ou 'administrador'
    email               # E-mail único (obrigatório)
    telefone            # Telefone de contato
    pergunta_seguranca_1  # Primeira pergunta de segurança
    resposta_seguranca_1  # Resposta da primeira pergunta
    pergunta_seguranca_2  # Segunda pergunta de segurança
    resposta_seguranca_2  # Resposta da segunda pergunta
    # + Campos do Django User (username, password, first_name, etc.)
```

### 📚 Curso

```python
class Curso(models.Model):
    id = UUIDField         # ID único (UUID)
    nome                   # Nome do curso (único)
    limite_km_mensal       # Limite de quilometragem mensal
    descricao              # Descrição do curso
    ativo                  # Status do curso (ativo/inativo)
    criado_em              # Data de criação
    atualizado_em          # Data da última atualização
```

**Métodos:**
- `get_km_utilizados_mes(ano, mes)` - Retorna KM utilizados no mês
- `tem_limite_disponivel(km_adicional, ano, mes)` - Verifica disponibilidade de KM

### 🚗 Veiculo

```python
class Veiculo(models.Model):
    id = UUIDField              # ID único (UUID)
    placa                       # Placa do veículo (única)
    modelo                      # Modelo do veículo
    marca                       # Marca do veículo
    ano                         # Ano de fabricação
    cor                         # Cor do veículo
    capacidade_passageiros      # Capacidade de passageiros
    observacoes                 # Observações adicionais
    ativo                       # Status do veículo (ativo/inativo)
    criado_em                   # Data de criação
    atualizado_em               # Data da última atualização
```

**Métodos:**
- `tem_conflito(data_inicio, data_fim, agendamento_id)` - Verifica conflitos de horário

### 📅 Agendamento

```python
class Agendamento(models.Model):
    id = UUIDField           # ID único (UUID)
    curso                    # ForeignKey para Curso
    professor                # ForeignKey para Usuario
    veiculo                  # ForeignKey para Veiculo
    data_inicio              # Data/hora de início
    data_fim                 # Data/hora de fim
    status                   # 'pendente', 'aprovado' ou 'reprovado'
    motivo_reprovacao        # Motivo da reprovação (opcional)
    aprovador                # ForeignKey para Usuario (quem aprovou)
    data_aprovacao           # Data da aprovação/reprovação
    criado_em                # Data de criação
    atualizado_em            # Data da última atualização
```

**Métodos:**
- `aprovar(aprovador)` - Aprova o agendamento
- `reprovar(aprovador, motivo)` - Reprova o agendamento
- `get_km_total()` - Retorna quilometragem total dos trajetos

### 🗺️ Trajeto

```python
class Trajeto(models.Model):
    id = UUIDField           # ID único (UUID)
    agendamento              # ForeignKey para Agendamento
    km_inicial               # Quilometragem inicial
    km_final                 # Quilometragem final
    descricao                # Descrição do trajeto
    data_registro            # Data de registro
    criado_em                # Data de criação
```

**Propriedades:**
- `km_percorridos` - Calcula a diferença entre KM final e inicial

## 👥 Colaboradores

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/HeitorLouzeiro">
        <img src="https://github.com/HeitorLouzeiro.png" width="100px;" alt="Heitor Louzeiro"/>
        <br />
        <sub><b>Heitor Louzeiro</b></sub>
      </a>
      <br />
      <sub>💻 Desenvolvedor</sub>
      <br />
      <a href="https://www.linkedin.com/in/heitor-louzeiro/">
        <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/>
      </a>
    </td>
  </tr>
</table>

## 🤝 Contribuição

1. **Fork** o projeto
2. Crie uma **branch** para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. **Commit** suas mudanças (`git commit -m 'Adiciona NovaFuncionalidade'`)
4. **Push** para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um **Pull Request**

### Diretrizes de Contribuição

- ✅ Siga a **PEP 8** para código Python
- ✅ Use **nomes descritivos** para variáveis e funções
- ✅ Adicione **docstrings** para classes e funções
- ✅ Escreva **testes** para novas funcionalidades
- ✅ Atualize a **documentação** quando necessário
- ✅ Use **commits semânticos**

### Commits Semânticos

```
feat: Nova funcionalidade
fix: Correção de bug
docs: Alteração na documentação
style: Formatação de código
refactor: Refatoração de código
test: Adição ou correção de testes
chore: Tarefas de manutenção
```

## 📜 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<div align="center">
<table>
  <tr>
    <td align="center">
      <strong>Heitor Louzeiro</strong><br/>
      <a href="https://github.com/HeitorLouzeiro">
        <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/>
      </a>
      <a href="https://www.linkedin.com/in/heitor-louzeiro/">
        <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/>
      </a>
    </td>
  </tr>
</table>

🚗 **Sistema de Agendamento de Veículos - Controle Total dos seus Agendamentos** 🚗

</div>
