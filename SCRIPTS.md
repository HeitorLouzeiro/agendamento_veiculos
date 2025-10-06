# 🚀 Scripts de Automação

Este projeto inclui scripts shell para facilitar o desenvolvimento e deploy. Todos os scripts são executáveis e incluem verificações de segurança.

## 📋 Scripts Disponíveis

### 🎯 `./start.sh` - Script Principal
Script completo com verificações e opções avançadas.

```bash
# Iniciar servidor completo (padrão)
./start.sh

# Opções disponíveis
./start.sh start    # Inicia servidor (mesmo que ./start.sh)
./start.sh data     # Apenas carrega dados de exemplo
./start.sh setup    # Apenas configuração inicial
./start.sh help     # Mostra ajuda
```

**Funcionalidades:**
- ✅ Ativa ambiente virtual automaticamente
- ✅ Verifica e aplica migrações
- ✅ Detecta porta disponível (8000-8005)
- ✅ Verifica superusuários existentes
- ✅ Opção para carregar dados de exemplo
- ✅ Interface colorida e informativa
- ✅ Tratamento de erros

### ⚡ `./dev.sh` - Desenvolvimento Rápido
Script minimalista para desenvolvimento rápido.

```bash
./dev.sh
```

**O que faz:**
- Ativa venv
- Aplica migrações
- Inicia servidor na porta 8000

### 🗄️ `./reset.sh` - Reset do Banco
Reset completo do banco de dados e migrações.

```bash
./reset.sh
```

**⚠️ CUIDADO:** Este script apaga TODOS os dados!

**O que faz:**
- Remove `db.sqlite3`
- Limpa arquivos de migração
- Recria migrações
- Aplica migrações
- Opção para carregar dados de exemplo

### 🛠️ `./setup.sh` - Setup Inicial
Configuração inicial completa para novos desenvolvedores.

```bash
./setup.sh
```

**Ideal para:**
- Primeiro setup do projeto
- Configuração em nova máquina
- Onboarding de desenvolvedores

**O que faz:**
- Verifica Python e pip
- Cria ambiente virtual
- Instala dependências
- **Cria arquivo `.env`** com configurações de desenvolvimento
- Executa migrações
- Carrega dados iniciais
- Configura permissões

## 🔧 Configuração de Ambiente

### 📄 Arquivo `.env`

O script `setup.sh` cria automaticamente um arquivo `.env` com configurações prontas para desenvolvimento:

```bash
# Após executar ./setup.sh
# O arquivo .env já está pronto para uso!
# Edite apenas se precisar personalizar
```

**Configurações essenciais incluídas:**
- ✅ `SECRET_KEY` - Chave secreta do Django
- ✅ `DEBUG` - Modo de desenvolvimento
- ✅ `ALLOWED_HOSTS` - Hosts permitidos
- ✅ `TIME_ZONE` - Fuso horário (America/Sao_Paulo)
- ✅ `LANGUAGE_CODE` - Idioma (pt-br)
- ✅ Arquivo limpo e enxuto (17 linhas)

### 🔒 Segurança

- ✅ `.env` está no `.gitignore` (não é versionado)
- ✅ Criado automaticamente com valores seguros
- ✅ Configurações prontas para desenvolvimento
- ✅ Comentários com exemplos para produção

## 🎨 Características dos Scripts

### 🌈 Interface Colorida
- 🔵 **AZUL**: Informações
- 🟢 **VERDE**: Sucessos
- 🟡 **AMARELO**: Avisos
- 🔴 **VERMELHO**: Erros
- 🟣 **ROXO**: Headers e destaques

### 🛡️ Verificações de Segurança
- Confirmação para ações destrutivas
- Verificação de diretório correto
- Detecção automática de ambiente virtual
- Verificação de dependências

### 🔧 Funcionalidades Inteligentes
- Detecção automática de porta disponível
- Criação automática de venv se não existir
- Instalação automática de dependências
- Verificação de superusuários

## 📖 Exemplos de Uso

### Primeiro Setup (Novo Desenvolvedor)
```bash
git clone <repo>
cd agendamento_veiculos
./setup.sh
```

### Desenvolvimento Diário
```bash
# Opção 1: Completa (recomendada)
./start.sh

# Opção 2: Rápida
./dev.sh
```

### Reset do Projeto
```bash
./reset.sh
```

### Carregar Apenas Dados
```bash
./start.sh data
```

## 🚨 Troubleshooting

### Script não executa
```bash
chmod +x *.sh
```

### Erro de ambiente virtual
```bash
rm -rf venv
./setup.sh
```

### Porta em uso
O `start.sh` detecta automaticamente portas disponíveis (8000-8005).

### Dependências em falta
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 💡 Dicas

1. **Use `./start.sh`** para desenvolvimento normal
2. **Use `./dev.sh`** quando precisar de velocidade máxima
3. **Use `./setup.sh`** uma vez por máquina/projeto
4. **Use `./reset.sh`** quando quiser começar do zero

## 🔄 Fluxo Recomendado

```bash
# 1. Setup inicial (uma vez)
./setup.sh

# 2. Desenvolvimento diário
./start.sh

# 3. Se precisar resetar
./reset.sh
```

---

💡 **Dica:** Todos os scripts incluem `--help` ou help para mostrar opções disponíveis.