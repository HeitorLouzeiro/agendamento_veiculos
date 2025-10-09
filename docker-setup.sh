#!/bin/bash

# Script para inicializar o projeto com Docker

echo "🚀 Configurando projeto com Docker..."

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "📄 Copiando arquivo de configuração .env.example para .env..."
    cp .env.example .env
    echo "✅ Arquivo .env criado. Edite-o conforme necessário."
fi

echo "🐳 Construindo imagens Docker..."
docker-compose build

echo "🗄️ Iniciando banco de dados PostgreSQL..."
docker-compose up -d db

echo "⏳ Aguardando PostgreSQL ficar pronto..."
sleep 10

echo "📊 Executando migrações do banco de dados..."
docker-compose run --rm web python manage.py migrate

echo "👤 Criando superusuário (opcional - pressione Ctrl+C para pular)..."
docker-compose run --rm web python manage.py createsuperuser

echo "✅ Configuração completa!"
echo ""
echo "Para iniciar a aplicação:"
echo "  - Desenvolvimento: docker-compose --profile dev up"
echo "  - Produção: docker-compose up"
echo ""
echo "Para parar os serviços:"
echo "  docker-compose down"