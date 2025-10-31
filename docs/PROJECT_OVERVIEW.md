# 📊 Visão Geral do Projeto - Sistema de Agendamento de Veículos UESPI

## 🎯 Objetivo do Sistema

Automatizar e gerenciar o processo de agendamento de veículos institucionais da UESPI, proporcionando controle, transparência e eficiência na utilização da frota.

---

## 📈 Principais Indicadores

### Funcionalidades Implementadas
- ✅ **100%** - Sistema de autenticação customizado
- ✅ **100%** - CRUD completo de veículos, cursos e agendamentos
- ✅ **100%** - Sistema de aprovação de agendamentos
- ✅ **100%** - Dashboard com estatísticas
- ✅ **100%** - Exportação de relatórios (Excel e PDF)
- ✅ **100%** - Notificações por email
- ✅ **100%** - Calendário de agendamentos
- ✅ **100%** - Deploy automatizado com Docker

### Tecnologias
- **Backend:** Django 5.2.7 + Python 3.12
- **Banco de Dados:** PostgreSQL 15
- **Frontend:** HTML5, CSS3, JavaScript
- **DevOps:** Docker + Docker Compose
- **Servidor:** Gunicorn + WhiteNoise

---

## 👥 Tipos de Usuários

### 1. Professor
**Permissões:**
- Criar agendamentos de veículos
- Visualizar próprios agendamentos
- Acompanhar status de aprovação
- Receber notificações por email
- Visualizar calendário de disponibilidade

### 2. Administrador
**Permissões:**
- Todas as permissões de professor
- Aprovar/Reprovar agendamentos
- Gerenciar usuários (CRUD)
- Gerenciar veículos (CRUD)
- Gerenciar cursos (CRUD)
- Gerar relatórios completos
- Exportar dados em Excel/PDF
- Visualizar dashboard com estatísticas

---

## 🏗️ Módulos do Sistema

### 1. Módulo de Autenticação (`usuarios/`)
- Registro com email institucional (`@*.uespi.br`)
- Ativação de conta via email
- Login/Logout
- Recuperação de senha
- Perfil de usuário

### 2. Módulo de Veículos (`veiculos/`)
- Cadastro de veículos
- Informações: placa, modelo, marca, ano, capacidade
- Status ativo/inativo
- Histórico de agendamentos

### 3. Módulo de Cursos (`cursos/`)
- Cadastro de cursos
- Controle de limite mensal de KM
- Vínculo com agendamentos
- Relatórios por curso

### 4. Módulo de Agendamentos (`agendamentos/`)
- Criação de agendamentos
- Seleção de veículo, data/hora
- Status: Pendente, Aprovado, Reprovado
- Validação de conflitos
- Cálculo de KM previstos

### 5. Módulo de Aprovação (`agendamentos/views/aprovacao_views.py`)
- Lista de agendamentos pendentes
- Aprovação em massa
- Reprovação com motivo
- Notificação automática

### 6. Módulo de Relatórios (`agendamentos/views/relatorio_views.py`)
- Relatório geral de agendamentos
- Relatório por curso
- Relatório por professor
- Filtros por data, status, curso
- Exportação Excel e PDF

### 7. Dashboard (`dashboard/`)
- Estatísticas em tempo real
- Gráficos e indicadores
- Resumo de agendamentos
- Veículos mais utilizados

---

## 🔄 Fluxo de Agendamento

```
1. Professor faz login no sistema
   ↓
2. Acessa "Novo Agendamento"
   ↓
3. Seleciona:
   - Curso
   - Veículo (verifica disponibilidade)
   - Data/Hora de início e fim
   - KM previsto
   - Destino/Motivo
   ↓
4. Sistema valida:
   - Disponibilidade do veículo
   - Conflitos de horário
   - Limite de KM do curso
   ↓
5. Agendamento criado com status "Pendente"
   ↓
6. Administrador recebe notificação
   ↓
7. Administrador aprova ou reprova
   ↓
8. Professor recebe notificação por email
   ↓
9. Status atualizado para "Aprovado" ou "Reprovado"
```

---

## 📊 Estatísticas do Código

### Estrutura
```
📁 Diretórios: ~30
📄 Arquivos Python: ~40
📝 Templates HTML: ~20
📦 Dependências: 20 pacotes principais
```

### Lines of Code (estimado)
```
Python (backend):     ~5.000 linhas
HTML (templates):     ~3.000 linhas
JavaScript:           ~500 linhas
CSS:                  ~1.000 linhas
Docker/Scripts:       ~500 linhas
------------------------
Total:                ~10.000 linhas
```

---

## 🚀 Deployment

### Ambientes Suportados

#### 1. Desenvolvimento Local
- Python + Django runserver
- SQLite ou PostgreSQL local
- Hot reload automático

#### 2. Produção com Docker (Recomendado)
- Docker Compose
- PostgreSQL em container
- Gunicorn como servidor WSGI
- WhiteNoise para arquivos estáticos
- Script automatizado de deploy

#### 3. Servidor de Produção
- Nginx como proxy reverso
- PostgreSQL dedicado
- Certificado SSL/HTTPS
- Backup automático

---

## 🔐 Segurança Implementada

### Autenticação e Autorização
- ✅ Senhas hasheadas (PBKDF2)
- ✅ Proteção CSRF
- ✅ Validação de email institucional
- ✅ Ativação de conta obrigatória
- ✅ Recuperação de senha segura
- ✅ Sistema de permissões do Django

### Validações
- ✅ Sanitização de inputs
- ✅ Validação de conflitos de agendamento
- ✅ Proteção contra SQL Injection (ORM Django)
- ✅ Proteção XSS (template engine Django)
- ✅ Validação de formulários no backend

### Configurações
- ✅ SECRET_KEY forte e única
- ✅ DEBUG=False em produção
- ✅ ALLOWED_HOSTS configurável
- ✅ HTTPS recomendado
- ✅ Variáveis de ambiente (.env)

---

## 📈 Escalabilidade

### Arquitetura Preparada Para:
- **Horizontal Scaling**: Múltiplas instâncias do container web
- **Database Scaling**: PostgreSQL suporta replicação
- **Caching**: Redis pode ser adicionado facilmente
- **Load Balancing**: Nginx pode distribuir carga
- **CDN**: Arquivos estáticos podem usar CDN

### Otimizações Implementadas
- Queries otimizadas com `select_related` e `prefetch_related`
- Paginação em todas as listagens
- Índices no banco de dados
- WhiteNoise para servir estáticos eficientemente
- Compressão de respostas

---

## 💻 Qualidade do Código

### Boas Práticas
- ✅ Código modular e reutilizável
- ✅ Separação de responsabilidades
- ✅ Views organizadas por funcionalidade
- ✅ Models com validações customizadas
- ✅ Forms com validações no backend
- ✅ Decorators para controle de acesso
- ✅ Constantes centralizadas
- ✅ Helpers e utilitários

### Padrões Django
- ✅ MTV (Model-Template-View)
- ✅ Class-Based Views
- ✅ Django ORM
- ✅ Template inheritance
- ✅ URL namespacing
- ✅ Static files management

---

## 📚 Documentação Disponível

| Arquivo | Descrição | Tamanho |
|---------|-----------|---------|
| **README.md** | Documentação completa do projeto | ~14 KB |
| **QUICKSTART.md** | Guia de início rápido | ~5.7 KB |
| **COMMANDS.md** | Referência de comandos úteis | ~11 KB |
| **EMAIL_CONFIG.md** | Configuração de email | ~4.6 KB |
| **LICENSE** | Licença MIT | - |

---

## 🎓 Casos de Uso

### Caso de Uso 1: Professor Agenda Veículo
```
Ator: Professor
Fluxo Principal:
1. Professor faz login
2. Acessa "Novo Agendamento"
3. Seleciona curso, veículo, data/hora
4. Informa KM previsto e destino
5. Submete o formulário
6. Sistema valida e cria agendamento
7. Status inicial: "Pendente"
8. Professor recebe confirmação
```

### Caso de Uso 2: Administrador Aprova Agendamento
```
Ator: Administrador
Fluxo Principal:
1. Admin faz login
2. Acessa "Aprovações Pendentes"
3. Visualiza detalhes do agendamento
4. Verifica disponibilidade e justificativa
5. Aprova o agendamento
6. Sistema atualiza status para "Aprovado"
7. Professor recebe notificação por email
```

### Caso de Uso 3: Geração de Relatório
```
Ator: Administrador
Fluxo Principal:
1. Admin acessa "Relatórios"
2. Seleciona tipo (Geral, Por Curso, Por Professor)
3. Define filtros (data, status, curso)
4. Visualiza relatório na tela
5. Exporta em Excel ou PDF
6. Download do arquivo
```

---

## 📞 Informações de Suporte

### Para Desenvolvedores
- **Documentação Django:** https://docs.djangoproject.com/
- **Docker Docs:** https://docs.docker.com/
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

### Para Usuários
- **Manual do Usuário:** (a ser criado)
- **FAQ:** (a ser criado)
- **Vídeos Tutoriais:** (a ser criado)

### Contato
- **Desenvolvedor:** Heitor Louzeiro
- **GitHub:** https://github.com/HeitorLouzeiro
- **Email:** Consultar perfil no GitHub

---

## 🗓️ Roadmap Futuro (Potencial)

### Versão 2.0 (Possíveis Melhorias)
- [ ] App mobile (React Native ou Flutter)
- [ ] API REST completa (Django REST Framework)
- [ ] Integração com calendário Google/Outlook
- [ ] Sistema de avaliação pós-uso do veículo
- [ ] Controle de manutenção de veículos
- [ ] Sistema de multas e penalidades
- [ ] Dashboard avançado com gráficos interativos
- [ ] Integração com GPS para tracking
- [ ] Notificações push
- [ ] Chat/Mensagens internas
- [ ] Sistema de reserva recorrente
- [ ] Integração com sistema de combustível

### Melhorias de Infraestrutura
- [ ] CI/CD com GitHub Actions
- [ ] Implementação de testes automatizados
- [ ] Monitoramento com Prometheus/Grafana
- [ ] Logs centralizados (ELK Stack)
- [ ] Kubernetes para orquestração
- [ ] Redis para caching
- [ ] Celery para tarefas assíncronas

---

## 📊 Métricas de Sucesso

### Objetivos Alcançados ✅
- Sistema 100% funcional
- Deploy automatizado
- Documentação completa
- Código modular e escalável
- Interface responsiva
- Segurança implementada

### KPIs (Key Performance Indicators)
- **Uptime:** Objetivo 99.9%
- **Tempo de Resposta:** < 200ms (média)
- **Satisfação do Usuário:** Meta > 4.5/5.0
- **Taxa de Aprovação:** Monitorar
- **Utilização de Veículos:** Maximizar

---

## 🏆 Diferenciais do Sistema

1. **Interface Intuitiva**: Fácil de usar para usuários não técnicos
2. **Deploy Automatizado**: Script completo de instalação
3. **Documentação Completa**: README profissional e guias detalhados
4. **Código Limpo**: Seguindo boas práticas Django
5. **Docker Ready**: Funciona out-of-the-box com containers
6. **Exportação Múltipla**: Excel e PDF para relatórios
7. **Sistema de Notificações**: Email automático para todas as ações
8. **Validações Robustas**: Previne conflitos e erros
9. **Dashboard Rico**: Estatísticas em tempo real
10. **Open Source**: Licença MIT, código disponível no GitHub

---

<div align="center">

**Sistema de Agendamento de Veículos - UESPI**

Desenvolvido com ❤️ e as melhores práticas de desenvolvimento web

*Python | Django | PostgreSQL | Docker*

---

Para mais informações, consulte:
- [README.md](README.md) - Documentação completa
- [QUICKSTART.md](QUICKSTART.md) - Início rápido
- [COMMANDS.md](COMMANDS.md) - Referência de comandos
- [EMAIL_CONFIG.md](EMAIL_CONFIG.md) - Configuração de email

</div>
