#!/bin/bash

# Script para criar o primeiro usuário administrador (superusuário)

echo "=========================================="
echo "Criação de Usuário Administrador"
echo "=========================================="
echo ""

# Verifica se o script está sendo executado no diretório correto
if [ ! -f "manage.py" ]; then
    echo "ERRO: Este script deve ser executado no diretório raiz do projeto Django."
    echo "Certifique-se de estar no diretório que contém o arquivo manage.py"
    exit 1
fi

echo "Este script criará um superusuário (administrador) para o sistema."
echo ""

# Solicita informações do usuário
read -p "Nome de usuário: " username
read -p "E-mail: " email
read -p "Nome: " first_name
read -p "Sobrenome: " last_name
read -sp "Senha: " password
echo ""
read -sp "Confirme a senha: " password2
echo ""

# Verifica se as senhas coincidem
if [ "$password" != "$password2" ]; then
    echo ""
    echo "ERRO: As senhas não coincidem!"
    exit 1
fi

# Cria o superusuário usando o shell do Django
echo ""
echo "Criando superusuário..."

python manage.py shell << EOF
from usuarios.models import Usuario
from django.db import IntegrityError

try:
    user = Usuario.objects.create_superuser(
        username='$username',
        email='$email',
        password='$password',
        first_name='$first_name',
        last_name='$last_name',
        tipo_usuario='administrador'
    )
    print('\n✓ Superusuário criado com sucesso!')
    print(f'  Usuário: {user.username}')
    print(f'  Nome: {user.get_full_name()}')
    print(f'  E-mail: {user.email}')
    print(f'  Tipo: Administrador')
except IntegrityError:
    print('\n✗ ERRO: Já existe um usuário com este nome de usuário.')
    exit(1)
except Exception as e:
    print(f'\n✗ ERRO: {str(e)}')
    exit(1)
EOF

echo ""
echo "=========================================="
echo "Você pode fazer login com as credenciais criadas."
echo "=========================================="
