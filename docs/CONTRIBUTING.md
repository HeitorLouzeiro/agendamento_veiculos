# 🤝 Guia de Contribuição - Sistema de Agendamento de Veículos

Obrigado por considerar contribuir para o Sistema de Agendamento de Veículos da UESPI! Este documento fornece diretrizes para contribuir com o projeto.

---

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Contribuir](#como-contribuir)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Padrões de Código](#padrões-de-código)
- [Processo de Pull Request](#processo-de-pull-request)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Melhorias](#sugerir-melhorias)

---

## 📜 Código de Conduta

### Nossos Compromissos

- Respeitar todas as pessoas, independentemente de origem
- Aceitar críticas construtivas
- Focar no que é melhor para a comunidade
- Demonstrar empatia com outros membros

### Comportamentos Inaceitáveis

- Linguagem ou imagens sexualizadas
- Trolling, insultos ou comentários depreciativos
- Assédio público ou privado
- Publicar informações privadas de terceiros

---

## 🚀 Como Contribuir

### Tipos de Contribuição

1. **Reportar Bugs**: Encontrou um problema? Abra uma issue!
2. **Sugerir Features**: Tem uma ideia? Compartilhe conosco!
3. **Melhorar Documentação**: Documentação sempre pode melhorar
4. **Corrigir Bugs**: Escolha uma issue e resolva
5. **Implementar Features**: Pegue uma feature da roadmap
6. **Code Review**: Revise Pull Requests de outros

### Onde Começar?

1. Leia a documentação completa ([README.md](README.md))
2. Configure o ambiente de desenvolvimento
3. Explore o código e familiarize-se com a estrutura
4. Procure issues marcadas como `good first issue` ou `help wanted`
5. Comente na issue que deseja trabalhar nela

---

## 💻 Configuração do Ambiente

### Pré-requisitos

- Python 3.12+
- Docker e Docker Compose (recomendado)
- Git
- Editor de código (VS Code recomendado)

### Configuração com Docker (Recomendado)

```bash
# 1. Fork o repositório no GitHub

# 2. Clone seu fork
git clone https://github.com/SEU_USUARIO/agendamento_veiculos.git
cd agendamento_veiculos

# 3. Adicione o repositório original como upstream
git remote add upstream https://github.com/HeitorLouzeiro/agendamento_veiculos.git

# 4. Torne o script executável
chmod +x scripts/deploy-production.sh

# 5. Execute o setup
./scripts/deploy-production.sh deploy

# 6. Crie um superusuário
docker-compose exec web python manage.py createsuperuser
```

### Configuração Local (Sem Docker)

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/agendamento_veiculos.git
cd agendamento_veiculos

# 2. Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
# Edite o .env conforme necessário

# 5. Execute migrações
python manage.py migrate

# 6. Crie superusuário
python manage.py createsuperuser

# 7. Inicie servidor
python manage.py runserver
```

---

## 📝 Padrões de Código

### Python (PEP 8)

#### Nomenclatura

```python
# Classes: PascalCase
class AgendamentoService:
    pass

# Funções e variáveis: snake_case
def calcular_km_total():
    total_km = 0
    return total_km

# Constantes: UPPER_SNAKE_CASE
MAX_KM_MENSAL = 1000

# Métodos privados: prefixo _
def _validar_interno():
    pass
```

#### Imports

```python
# 1. Biblioteca padrão
import os
import sys
from datetime import datetime

# 2. Bibliotecas de terceiros
from django.db import models
from django.contrib.auth import login

# 3. Imports locais
from .models import Agendamento
from .forms import AgendamentoForm
```

#### Docstrings

```python
def criar_agendamento(curso_id, veiculo_id, data_inicio):
    """
    Cria um novo agendamento de veículo.
    
    Args:
        curso_id (UUID): ID do curso
        veiculo_id (UUID): ID do veículo
        data_inicio (datetime): Data/hora de início
        
    Returns:
        Agendamento: Objeto agendamento criado
        
    Raises:
        ValidationError: Se houver conflito de horário
    """
    pass
```

### HTML/Templates Django

```html
{# Use indentação de 2 espaços #}
{% extends "base.html" %}

{% block title %}
  Título da Página
{% endblock %}

{% block content %}
  <div class="container">
    <h1>Título</h1>
    {# Comentário em template #}
    {% for item in items %}
      <p>{{ item.nome }}</p>
    {% endfor %}
  </div>
{% endblock %}
```

### JavaScript

```javascript
// Use const/let, não var
const API_URL = '/api/agendamentos/';

// Funções: camelCase
function calcularDuracao(inicio, fim) {
  return fim - inicio;
}

// Classes: PascalCase
class CalendarioManager {
  constructor() {
    this.eventos = [];
  }
}
```

### Git Commit Messages

```bash
# Formato:
tipo(escopo): descrição curta

# Tipos:
feat: Nova funcionalidade
fix: Correção de bug
docs: Alteração em documentação
style: Formatação, sem mudança de código
refactor: Refatoração de código
test: Adição ou correção de testes
chore: Tarefas de manutenção

# Exemplos:
feat(agendamentos): adiciona validação de conflito de horários
fix(veiculos): corrige filtro de veículos disponíveis
docs(readme): atualiza instruções de instalação
refactor(models): melhora queries do Agendamento
test(agendamentos): adiciona testes de validação
```

---

## 🔄 Processo de Pull Request

### 1. Crie uma Branch

```bash
# Atualize sua main
git checkout main
git pull upstream main

# Crie branch para sua feature/fix
git checkout -b feat/minha-feature
# ou
git checkout -b fix/corrigir-bug
```

### 2. Desenvolva e Teste

```bash
# Faça suas alterações

# Verifique código
python manage.py check
# ou
docker-compose exec web python manage.py check

# Execute o sistema e teste manualmente
python manage.py runserver
# ou
docker-compose up -d
```

### 3. Commit e Push

```bash
# Adicione arquivos
git add .

# Commit com mensagem descritiva
git commit -m "feat(agendamentos): adiciona validação de horário"

# Push para seu fork
git push origin feat/minha-feature
```

### 4. Abra Pull Request

1. Vá para o seu fork no GitHub
2. Clique em "Compare & pull request"
3. Preencha o template de PR:

```markdown
## Descrição
Descrição clara do que foi implementado/corrigido

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Breaking change
- [ ] Documentação

## Como Testar
1. Passo 1
2. Passo 2
3. Resultado esperado

## Checklist
- [ ] Código segue os padrões do projeto
- [ ] Documentação foi atualizada
- [ ] Sistema foi testado manualmente
- [ ] Não há warnings ou erros
```

### 5. Review e Merge

- Aguarde review dos mantenedores
- Responda comentários e faça ajustes se necessário
- Após aprovação, será feito o merge

---

## 🐛 Reportar Bugs

### Antes de Reportar

1. Verifique se já não existe uma issue sobre o bug
2. Certifique-se de estar usando a versão mais recente
3. Tente reproduzir o bug em ambiente limpo

### Template de Bug Report

```markdown
**Descrição do Bug**
Descrição clara e concisa do bug.

**Para Reproduzir**
Passos para reproduzir o comportamento:
1. Vá para '...'
2. Clique em '....'
3. Role até '....'
4. Veja o erro

**Comportamento Esperado**
O que você esperava que acontecesse.

**Screenshots**
Se aplicável, adicione screenshots.

**Ambiente:**
- OS: [e.g. Ubuntu 22.04]
- Browser: [e.g. Chrome 120]
- Python: [e.g. 3.12]
- Django: [e.g. 5.2.7]

**Contexto Adicional**
Qualquer outro contexto sobre o problema.
```

---

## 💡 Sugerir Melhorias

### Template de Feature Request

```markdown
**Sua feature resolve um problema?**
Descrição clara do problema.

**Descreva a solução desejada**
Descrição clara do que você quer que aconteça.

**Descreva alternativas consideradas**
Alternativas que você considerou.

**Contexto Adicional**
Screenshots, mockups, etc.
```

---

## 📚 Recursos Úteis

### Documentação

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Best Practices](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Docker Documentation](https://docs.docker.com/)

### Ferramentas Recomendadas

- **VS Code** com extensões:
  - Python
  - Django
  - GitLens
  - Docker
- **DBeaver** para gerenciar PostgreSQL
- **Postman** para testar APIs
- **GitKraken** para gerenciar Git visualmente

---

## 🎯 Áreas que Precisam de Ajuda

### Alta Prioridade

- [ ] Implementação de testes automatizados
- [ ] Documentação de API (se houver)
- [ ] Internacionalização (i18n)
- [ ] Acessibilidade (WCAG)

### Média Prioridade

- [ ] Melhorias de UI/UX
- [ ] Otimização de queries
- [ ] Refatoração de código legado
- [ ] Adicionar logs

### Baixa Prioridade

- [ ] Comentários no código
- [ ] Exemplos de uso
- [ ] Guias em vídeo
- [ ] Tradução da documentação

---

## ❓ FAQ

### Posso trabalhar em uma feature sem abrir issue?

Preferível abrir issue primeiro para discussão e evitar trabalho duplicado.

### Quanto tempo leva para revisar um PR?

Geralmente 3-7 dias. Se urgente, mencione nas descrição.

### Preciso assinar CLA?

Não, este projeto usa licença MIT e não requer CLA.

### Posso usar este código em outro projeto?

Sim, seguindo os termos da licença MIT.

---

## 🏆 Reconhecimento

Todos os contribuidores serão listados em:
- README.md (seção de agradecimentos)
- GitHub Contributors
- Release notes (para contribuições significativas)

---

## 📞 Contato

- **Issues:** [GitHub Issues](https://github.com/HeitorLouzeiro/agendamento_veiculos/issues)
- **Discussions:** [GitHub Discussions](https://github.com/HeitorLouzeiro/agendamento_veiculos/discussions)
- **Email:** Consultar perfil do desenvolvedor

---

<div align="center">

**Obrigado por contribuir!** 🎉

Juntos tornamos este projeto melhor para toda a comunidade UESPI.

</div>
