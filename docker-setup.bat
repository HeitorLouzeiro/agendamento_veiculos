@echo off
REM Script para inicializar o projeto com Docker no Windows

echo 🚀 Configurando projeto com Docker...

REM Verificar se o arquivo .env existe
if not exist .env (
    echo 📄 Copiando arquivo de configuração .env.example para .env...
    copy .env.example .env
    echo ✅ Arquivo .env criado. Edite-o conforme necessário.
)

echo 🐳 Construindo imagens Docker...
docker-compose build

echo 🗄️ Iniciando banco de dados PostgreSQL...
docker-compose up -d db

echo ⏳ Aguardando PostgreSQL ficar pronto...
timeout /t 10 /nobreak > nul

echo 📊 Executando migrações do banco de dados...
docker-compose run --rm web python manage.py migrate

echo 👤 Criando superusuário (opcional - pressione Ctrl+C para pular)...
docker-compose run --rm web python manage.py createsuperuser

echo ✅ Configuração completa!
echo.
echo Para iniciar a aplicação:
echo   - Desenvolvimento: docker-compose --profile dev up
echo   - Produção: docker-compose up
echo.
echo Para parar os serviços:
echo   docker-compose down

pause