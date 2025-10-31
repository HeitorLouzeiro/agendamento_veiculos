# 🚀 Guia de Início Rápido - Sistema de Agendamento de Veículos

Este guia fornece instruções passo a passo para colocar o sistema em funcionamento rapidamente.

## ⚡ Início Rápido com Docker (5 minutos)

### Pré-requisitos
- Docker e Docker Compose instalados
- Git instalado

### Passo 1: Clone o repositório
```bash
git clone https://github.com/HeitorLouzeiro/agendamento_veiculos.git
cd agendamento_veiculos
```

### Passo 2: Torne o script executável
```bash
chmod +x scripts/deploy-production.sh
```

### Passo 3: Execute o deploy
```bash
./scripts/deploy-production.sh
```

Escolha a opção **1** (Deploy completo) no menu interativo.

### Passo 4: Crie um superusuário
Quando solicitado pelo script, digite **s** para criar um superusuário e forneça:
- Username (ex: admin)
- Email (ex: admin@uespi.br)
- Password (escolha uma senha forte)

### Passo 5: Acesse o sistema
Abra seu navegador e acesse:
```
http://localhost:8000
```

🎉 **Pronto!** O sistema está funcionando!

---

## 📋 Primeiros Passos no Sistema

### 1. Faça login como administrador
- Acesse: http://localhost:8000/login/
- Use as credenciais criadas no passo 4

### 2. Configure os dados iniciais

#### a) Cadastre cursos
1. Vá em **Cursos** → **Novo Curso**
2. Preencha:
   - Nome do curso (ex: "Licenciatura em Física")
   - Limite de KM mensal (ex: 1000)
   - Descrição (opcional)

#### b) Cadastre veículos
1. Vá em **Veículos** → **Novo Veículo**
2. Preencha:
   - Placa (ex: ABC-1234)
   - Modelo (ex: "Fiat Uno")
   - Marca (ex: "Fiat")
   - Ano (ex: 2020)
   - Capacidade de passageiros (ex: 5)

#### c) Cadastre professores (se necessário)
1. Vá em **Admin** → **Usuários**
2. Clique em **Adicionar Usuário**
3. Preencha os dados e selecione tipo "Professor"

### 3. Teste um agendamento
1. Faça logout e crie uma conta de professor
2. Faça login como professor
3. Vá em **Agendamentos** → **Novo Agendamento**
4. Preencha os dados e submeta
5. Faça login como admin novamente
6. Aprove o agendamento em **Aprovações Pendentes**

---

## 🔧 Comandos Úteis

### Ver logs em tempo real
```bash
docker-compose logs -f web
```

### Parar o sistema
```bash
docker-compose down
```

### Reiniciar o sistema
```bash
docker-compose up -d
```

### Criar backup do banco de dados
```bash
docker-compose exec db pg_dump -U postgres agendamento_veiculos > backup_$(date +%Y%m%d).sql
```

### Acessar o shell do Django
```bash
docker-compose exec web python manage.py shell
```

### Executar comandos Django
```bash
docker-compose exec web python manage.py <comando>
```

---

## 🐛 Solução Rápida de Problemas

### Porta 8000 já está em uso
```bash
# Parar processo usando a porta
sudo lsof -i :8000
kill -9 <PID>
```

### Container não inicia
```bash
# Ver logs
docker-compose logs web

# Rebuild completo
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Esqueci a senha do superusuário
```bash
docker-compose exec web python manage.py changepassword <username>
```

### Resetar o banco de dados (CUIDADO: apaga todos os dados!)
```bash
docker-compose down -v
docker volume rm agendamento_veiculos_postgres_data
./scripts/deploy-production.sh deploy
```

---

## 📱 Acessos Rápidos

| Funcionalidade | URL |
|----------------|-----|
| Página inicial | http://localhost:8000 |
| Login | http://localhost:8000/login/ |
| Admin Django | http://localhost:8000/admin/ |
| Dashboard | http://localhost:8000/dashboard/ |
| Agendamentos | http://localhost:8000/agendamentos/ |
| Veículos | http://localhost:8000/veiculos/ |
| Cursos | http://localhost:8000/cursos/ |

---

## 📧 Configurar Email de Produção (Opcional)

### 1. Edite o arquivo .env
```bash
nano .env
# ou
vim .env
```

### 2. Configure o SMTP do Gmail
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app-do-gmail
DEFAULT_FROM_EMAIL=noreply@uespi.br
```

### 3. Gere uma senha de app do Gmail
1. Acesse: https://myaccount.google.com/apppasswords
2. Gere uma senha para "Outros (nome personalizado)"
3. Copie a senha gerada
4. Cole no `EMAIL_HOST_PASSWORD`

### 4. Reinicie o sistema
```bash
docker-compose restart web
```

---

## 🔐 Checklist de Segurança para Produção

Antes de colocar em produção em um servidor público:

- [ ] Alterar `SECRET_KEY` no `.env` para uma chave única e forte
- [ ] Configurar `DEBUG=False` no `.env`
- [ ] Configurar `ALLOWED_HOSTS` com o domínio real no `.env`
- [ ] Usar senha forte para o banco de dados PostgreSQL
- [ ] Configurar HTTPS com certificado SSL (Let's Encrypt + Nginx)
- [ ] Configurar backup automático do banco de dados
- [ ] Configurar firewall (apenas portas 80, 443 abertas)
- [ ] Configurar SMTP real para envio de emails
- [ ] Revisar permissões de arquivos e diretórios
- [ ] Configurar logs e monitoramento

---

## 📚 Próximos Passos

1. Leia a documentação completa em [README.md](../README.md)
2. Configure email institucional seguindo [EMAIL_CONFIG.md](../EMAIL_CONFIG.md)
3. Personalize templates em `templates/`
4. Ajuste configurações em `agendamento_veiculos/settings.py`
5. Explore o código fonte para customizações

---

## 🆘 Precisa de Ajuda?

- 📖 Documentação completa: [README.md](../README.md)
- 🐛 Relatar bugs: [GitHub Issues](https://github.com/HeitorLouzeiro/agendamento_veiculos/issues)
- 💬 Comunidade Django: https://www.djangoproject.com/community/
- 📧 Email do desenvolvedor: Verifique o perfil no GitHub

---

<div align="center">

**Desenvolvido com ❤️ para a UESPI**

⭐ Se este guia foi útil, considere dar uma estrela no projeto!

</div>
