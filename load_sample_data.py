#!/usr/bin/env python
"""
Script para carregar dados de exemplo no sistema
"""
import os
import django
from datetime import datetime, timedelta

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agendamento_veiculos.settings')
django.setup()

from usuarios.models import Usuario
from cursos.models import Curso
from veiculos.models import Veiculo
from agendamentos.models import Agendamento, Trajeto

def criar_dados_exemplo():
    print("=" * 50)
    print("Carregando dados de exemplo...")
    print("=" * 50)
    
    # Criar curso de exemplo
    print("\n1. Criando curso de exemplo...")
    curso, created = Curso.objects.get_or_create(
        nome="Engenharia Mecânica",
        defaults={
            'limite_km_mensal': 1000,
            'descricao': 'Curso de Engenharia Mecânica - Atividades práticas',
            'ativo': True
        }
    )
    if created:
        print(f"   ✓ Curso criado: {curso.nome}")
    else:
        print(f"   → Curso já existe: {curso.nome}")
    
    # Criar segundo curso
    curso2, created = Curso.objects.get_or_create(
        nome="Engenharia Civil",
        defaults={
            'limite_km_mensal': 800,
            'descricao': 'Curso de Engenharia Civil - Visitas técnicas',
            'ativo': True
        }
    )
    if created:
        print(f"   ✓ Curso criado: {curso2.nome}")
    else:
        print(f"   → Curso já existe: {curso2.nome}")
    
    # Criar veículo de exemplo
    print("\n2. Criando veículo de exemplo...")
    veiculo, created = Veiculo.objects.get_or_create(
        placa="ABC-1234",
        defaults={
            'modelo': 'Sprinter',
            'marca': 'Mercedes-Benz',
            'ano': 2022,
            'cor': 'Branco',
            'capacidade_passageiros': 15,
            'observacoes': 'Van para transporte de alunos',
            'ativo': True
        }
    )
    if created:
        print(f"   ✓ Veículo criado: {veiculo.placa} - {veiculo.marca} {veiculo.modelo}")
    else:
        print(f"   → Veículo já existe: {veiculo.placa}")
    
    # Criar segundo veículo
    veiculo2, created = Veiculo.objects.get_or_create(
        placa="XYZ-5678",
        defaults={
            'modelo': 'Hilux',
            'marca': 'Toyota',
            'ano': 2023,
            'cor': 'Prata',
            'capacidade_passageiros': 5,
            'observacoes': 'Caminhonete para trabalhos de campo',
            'ativo': True
        }
    )
    if created:
        print(f"   ✓ Veículo criado: {veiculo2.placa} - {veiculo2.marca} {veiculo2.modelo}")
    else:
        print(f"   → Veículo já existe: {veiculo2.placa}")
    
    # Criar professor de exemplo
    print("\n3. Criando professor de exemplo...")
    professor, created = Usuario.objects.get_or_create(
        username="professor1",
        defaults={
            'email': 'professor1@exemplo.com',
            'first_name': 'João',
            'last_name': 'Silva',
            'tipo_usuario': 'professor',
            'telefone': '(11) 98765-4321'
        }
    )
    if created:
        professor.set_password('senha123')
        professor.save()
        print(f"   ✓ Professor criado: {professor.get_full_name()} (username: {professor.username}, senha: senha123)")
    else:
        print(f"   → Professor já existe: {professor.get_full_name()}")
    
    # Criar agendamento de exemplo
    print("\n4. Criando agendamento de exemplo...")
    data_inicio = datetime.now() + timedelta(days=7)
    data_inicio = data_inicio.replace(hour=8, minute=0, second=0, microsecond=0)
    data_fim = data_inicio.replace(hour=17, minute=0)
    
    agendamento, created = Agendamento.objects.get_or_create(
        curso=curso,
        professor=professor,
        veiculo=veiculo,
        data_inicio=data_inicio,
        defaults={
            'data_fim': data_fim,
            'status': 'pendente',
            'observacoes': 'Visita técnica à fábrica'
        }
    )
    
    if created:
        print(f"   ✓ Agendamento criado: {agendamento.curso.nome} - {agendamento.data_inicio.strftime('%d/%m/%Y')}")
        
        # Criar trajeto para o agendamento
        trajeto = Trajeto.objects.create(
            agendamento=agendamento,
            origem='Campus Universitário',
            destino='Fábrica ABC Ltda',
            data_saida=data_inicio,
            data_chegada=data_inicio.replace(hour=12, minute=0),
            quilometragem=45,
            descricao='Ida para visita técnica na fábrica'
        )
        print(f"   ✓ Trajeto criado: {trajeto.origem} → {trajeto.destino} ({trajeto.quilometragem} km)")
        
        trajeto2 = Trajeto.objects.create(
            agendamento=agendamento,
            origem='Fábrica ABC Ltda',
            destino='Campus Universitário',
            data_saida=data_inicio.replace(hour=14, minute=0),
            data_chegada=data_fim,
            quilometragem=45,
            descricao='Retorno ao campus'
        )
        print(f"   ✓ Trajeto criado: {trajeto2.origem} → {trajeto2.destino} ({trajeto2.quilometragem} km)")
    else:
        print(f"   → Agendamento já existe")
    
    print("\n" + "=" * 50)
    print("Dados de exemplo carregados com sucesso!")
    print("=" * 50)
    print("\nResumo:")
    print(f"  • Cursos: {Curso.objects.count()}")
    print(f"  • Veículos: {Veiculo.objects.count()}")
    print(f"  • Professores: {Usuario.objects.filter(tipo_usuario='professor').count()}")
    print(f"  • Agendamentos: {Agendamento.objects.count()}")
    print("\nCredenciais de teste:")
    print("  Professor: username='professor1', senha='senha123'")
    print("\nPara criar um administrador, execute: ./create_admin.sh")
    print("=" * 50)

if __name__ == '__main__':
    criar_dados_exemplo()
