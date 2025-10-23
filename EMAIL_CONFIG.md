# Configuração de Email para Ativação de Conta

## Visão Geral

O sistema agora exige que novos usuários:
1. Se registrem com um **email institucional da UESPI** (formato: `@*.uespi.br`)
2. **Ativem sua conta** através de um link enviado por email

## Validação de Email Institucional

Os seguintes formatos de email são aceitos:
- `usuario@uespi.br`
- `usuario@aluno.uespi.br`
- `usuario@professor.uespi.br`
- Qualquer subdomínio: `usuario@[qualquer].uespi.br`

## Fluxo de Registro

1. **Usuário se registra** → Conta criada como **inativa** (`is_active=False`)
2. **Sistema envia email** com link de ativação (válido por 24 horas)
3. **Usuário clica no link** → Conta é **ativada** (`is_active=True`)
4. **Usuário pode fazer login** no sistema

## Configuração de Email (Desenvolvimento)

Por padrão, o sistema usa o **Console Backend** que exibe os emails no terminal.

### Arquivo `.env`

```env
# Email Configuration - Desenvolvimento (emails no console)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@uespi.br
```

## Configuração de Email (Produção)

Para ambiente de produção, configure um servidor SMTP real.

### Exemplo: Gmail SMTP

```env
# Email Configuration - Produção
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
DEFAULT_FROM_EMAIL=noreply@uespi.br
```

**Nota:** Para Gmail, você precisa:
1. Ativar "Verificação em duas etapas"
2. Gerar uma "Senha de app"
3. Usar a senha de app no `EMAIL_HOST_PASSWORD`

### Exemplo: Servidor SMTP Institucional

```env
# Email Configuration - SMTP UESPI
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.uespi.br
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=usuario@uespi.br
EMAIL_HOST_PASSWORD=sua-senha
DEFAULT_FROM_EMAIL=noreply@uespi.br
```

## Migrações do Banco de Dados

Execute as migrações para adicionar os campos necessários:

```bash
# Ativar ambiente virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Executar migrações
python manage.py migrate
```

## Testando em Desenvolvimento

Com o Console Backend ativo, os emails aparecerão no terminal onde o servidor está rodando:

```bash
python manage.py runserver
```

Ao registrar um usuário, você verá algo como:

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Ative sua conta - Sistema de Agendamento UESPI
From: noreply@uespi.br
To: usuario@professor.uespi.br
Date: ...

Olá, João Silva!

Obrigado por se registrar no Sistema de Agendamento de Veículos da UESPI.

Para ativar sua conta, clique no link abaixo:
http://localhost:8000/usuarios/ativar-conta/abc123...xyz789/

Este link é válido por 24 horas.
...
```

Copie o link e acesse no navegador para ativar a conta.

## Reenviar Link de Ativação

Se o usuário não receber o email ou o link expirar:
1. Acesse a página de login
2. Clique em "Reenviar link de ativação"
3. Informe o email cadastrado
4. Um novo link será enviado

## Segurança

- ✅ Tokens de ativação são únicos e aleatórios (64 caracteres)
- ✅ Tokens expiram após 24 horas
- ✅ Tokens são limpos após uso
- ✅ Usuários inativos não podem fazer login
- ✅ Sistema não revela se um email existe ou não (segurança)

## Administração

### Ativar Usuário Manualmente (Django Admin)

Se necessário, administradores podem ativar usuários pelo Django Admin:

1. Acesse `/admin/`
2. Vá em "Usuários"
3. Selecione o usuário
4. Marque "Ativo" (is_active)
5. Salve

### Criar Superusuário

Superusuários são criados ativos por padrão:

```bash
python manage.py createsuperuser
```

## URLs Disponíveis

- `/usuarios/registro/` - Registro de novo usuário
- `/usuarios/ativar-conta/<token>/` - Ativação de conta
- `/usuarios/reenviar-ativacao/` - Reenviar link de ativação
- `/usuarios/login/` - Login

## Troubleshooting

### Email não está sendo enviado

1. Verifique as configurações no `.env`
2. Verifique se o servidor SMTP está acessível
3. Verifique credenciais (usuário e senha)
4. Verifique firewall/portas

### Token expirado

- Usuário deve solicitar novo link em "Reenviar link de ativação"

### Email não chega

1. Verifique pasta de spam
2. Verifique se o email do remetente está correto
3. Verifique logs do servidor SMTP

### Usuário não consegue fazer login

- Verifique se a conta está ativa (`is_active=True`)
- Verifique no Django Admin ou banco de dados
