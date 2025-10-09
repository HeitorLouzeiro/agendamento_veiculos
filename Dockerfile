# Use uma imagem oficial do Python como base
FROM python:3.12-slim

# Defina variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instale dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Configure o diretório de trabalho
WORKDIR /app

# Copie os arquivos de dependências
COPY requirements.txt /app/

# Instale as dependências Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copie o código da aplicação
COPY . /app/

# Exponha a porta que a aplicação usará
EXPOSE 8000

# Comando padrão para executar a aplicação
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "agendamento_veiculos.wsgi:application"]