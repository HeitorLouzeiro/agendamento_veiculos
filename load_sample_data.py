#!/usr/bin/env python
"""
Script para carregar dados de exemplo no sistema usando Faker
Gera dados realistas para desenvolvimento e testes
"""
from veiculos.models import Veiculo
from usuarios.models import Usuario
from cursos.models import Curso
from agendamentos.models import Agendamento, Trajeto
from faker import Faker
import django
import os
import random
import sys
from datetime import datetime, timedelta

# Configura o Django ANTES de importar os models
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'agendamento_veiculos.settings')


django.setup()

# Agora importa os models e Faker


# Inicializa Faker com localização brasileira
fake = Faker('pt_BR')


def criar_cursos():
    """Cria cursos de exemplo usando dados realistas"""
    print("\n📚 [1/5] Criando cursos...")

    cursos_data = [
        {
            'nome': 'Engenharia Mecânica',
            'limite_km_mensal': 1000,
            'descricao': 'Atividades práticas e visitas técnicas'
        },
        {
            'nome': 'Engenharia Civil',
            'limite_km_mensal': 800,
            'descricao': 'Visitas a obras e canteiros'
        },
        {
            'nome': 'Engenharia Elétrica',
            'limite_km_mensal': 600,
            'descricao': 'Visitas a usinas e subestações'
        },
        {
            'nome': 'Arquitetura e Urbanismo',
            'limite_km_mensal': 900,
            'descricao': 'Estudos de campo e visitas arquitetônicas'
        },
        {
            'nome': 'Administração',
            'limite_km_mensal': 500,
            'descricao': 'Visitas empresariais e eventos'
        },
    ]

    cursos_criados = []
    for curso_data in cursos_data:
        curso, created = Curso.objects.get_or_create(
            nome=curso_data['nome'],
            defaults={
                'limite_km_mensal': curso_data['limite_km_mensal'],
                'descricao': curso_data['descricao'],
                'ativo': True
            }
        )
        if created:
            print(f"   ✓ {curso.nome} (Limite: {curso.limite_km_mensal}km)")
            cursos_criados.append(curso)
        else:
            print(f"   → {curso.nome} (já existe)")
            cursos_criados.append(curso)

    return cursos_criados


def criar_veiculos():
    """Cria veículos de exemplo com dados realistas"""
    print("\n🚗 [2/5] Criando veículos...")

    veiculos_data = [
        {
            'placa': 'ABC-1234', 'modelo': 'Sprinter', 'marca': 'Mercedes',
            'ano': 2022, 'cor': 'Branco', 'capacidade': 15,
            'obs': 'Van para transporte de grupos'
        },
        {
            'placa': 'XYZ-5678', 'modelo': 'Hilux', 'marca': 'Toyota',
            'ano': 2023, 'cor': 'Prata', 'capacidade': 5,
            'obs': 'Caminhonete para trabalhos de campo'
        },
        {
            'placa': 'DEF-9012', 'modelo': 'Ducato', 'marca': 'Fiat',
            'ano': 2021, 'cor': 'Branco', 'capacidade': 16,
            'obs': 'Van para viagens longas'
        },
        {
            'placa': 'GHI-3456', 'modelo': 'Kombi', 'marca': 'Volkswagen',
            'ano': 2014, 'cor': 'Branco', 'capacidade': 9,
            'obs': 'Transporte para pequenos grupos'
        },
        {
            'placa': 'JKL-7890', 'modelo': 'Master', 'marca': 'Renault',
            'ano': 2020, 'cor': 'Cinza', 'capacidade': 16,
            'obs': 'Van para eventos e visitas técnicas'
        },
    ]

    veiculos_criados = []
    for v_data in veiculos_data:
        veiculo, created = Veiculo.objects.get_or_create(
            placa=v_data['placa'],
            defaults={
                'modelo': v_data['modelo'],
                'marca': v_data['marca'],
                'ano': v_data['ano'],
                'cor': v_data['cor'],
                'capacidade_passageiros': v_data['capacidade'],
                'observacoes': v_data['obs'],
                'ativo': True
            }
        )
        if created:
            print(f"   ✓ {veiculo.placa} - {veiculo.marca} "
                  f"{veiculo.modelo} ({veiculo.capacidade_passageiros} "
                  f"passageiros)")
            veiculos_criados.append(veiculo)
        else:
            print(f"   → {veiculo.placa} (já existe)")
            veiculos_criados.append(veiculo)

    return veiculos_criados


def criar_professores(quantidade=10):
    """Cria professores com dados realistas usando Faker"""
    print(f"\n👨‍🏫 [3/5] Criando {quantidade} professores...")

    professores_criados = []
    for i in range(quantidade):
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = f"prof{i+1:02d}"

        professor, created = Usuario.objects.get_or_create(
            username=username,
            defaults={
                'email': fake.email(),
                'first_name': first_name,
                'last_name': last_name,
                'tipo_usuario': 'professor',
                'telefone': fake.phone_number()
            }
        )

        if created:
            professor.set_password('senha123')
            professor.save()
            print(f"   ✓ {professor.get_full_name()} "
                  f"(user: {username}, senha: senha123)")
            professores_criados.append(professor)
        else:
            professores_criados.append(professor)

    return professores_criados


def criar_agendamentos(cursos, veiculos, professores, quantidade=20):
    """Cria agendamentos realistas com trajetos usando Faker"""
    print(f"\n📅 [4/5] Criando {quantidade} agendamentos...")

    # Locais comuns para trajetos
    locais_origem = [
        'Campus Universitário', 'Centro de Pesquisa',
        'Laboratório Central', 'Faculdade de Engenharia'
    ]

    locais_destino = [
        f"Empresa {fake.company()}" for _ in range(15)
    ] + [
        'Fábrica de Componentes Automotivos',
        'Usina Hidrelétrica',
        'Canteiro de Obras Residencial',
        'Shopping Center em Construção',
        'Parque Industrial'
    ]

    status_opcoes = ['pendente', 'aprovado', 'reprovado']
    agendamentos_criados = 0

    for i in range(quantidade):
        # Gera data aleatória (entre 30 dias atrás e 60 dias à frente)
        dias = random.randint(-30, 60)
        data_base = datetime.now() + timedelta(days=dias)

        # Horários realistas
        hora_inicio = random.choice([7, 8, 9, 13, 14])
        hora_fim = hora_inicio + random.randint(4, 9)

        data_inicio = data_base.replace(
            hour=hora_inicio, minute=0, second=0, microsecond=0
        )
        data_fim = data_base.replace(
            hour=min(hora_fim, 23), minute=0, second=0, microsecond=0
        )

        # Seleciona aleatoriamente
        curso = random.choice(cursos)
        veiculo = random.choice(veiculos)
        professor = random.choice(professores)
        status = random.choice(status_opcoes)

        # Cria agendamento
        try:
            agendamento = Agendamento.objects.create(
                curso=curso,
                professor=professor,
                veiculo=veiculo,
                data_inicio=data_inicio,
                data_fim=data_fim,
                status=status,
                observacoes=fake.sentence(nb_words=10),
                motivo_reprovacao=(
                    fake.sentence(nb_words=15)
                    if status == 'reprovado' else ''
                )
            )

            # Cria trajetos (ida e volta)
            origem = random.choice(locais_origem)
            destino = random.choice(locais_destino)
            km = random.randint(15, 100)

            # Trajeto de ida
            hora_saida_ida = data_inicio
            hora_chegada_ida = data_inicio + timedelta(
                hours=random.randint(2, 4)
            )

            Trajeto.objects.create(
                agendamento=agendamento,
                origem=origem,
                destino=destino,
                data_saida=hora_saida_ida,
                data_chegada=hora_chegada_ida,
                quilometragem=km,
                descricao=f"Ida para {destino}"
            )

            # Trajeto de volta
            hora_saida_volta = hora_chegada_ida + timedelta(
                hours=random.randint(2, 5)
            )
            hora_chegada_volta = min(
                hora_saida_volta + timedelta(hours=random.randint(2, 4)),
                data_fim
            )

            Trajeto.objects.create(
                agendamento=agendamento,
                origem=destino,
                destino=origem,
                data_saida=hora_saida_volta,
                data_chegada=hora_chegada_volta,
                quilometragem=km,
                descricao=f"Retorno de {destino}"
            )

            agendamentos_criados += 1
            if agendamentos_criados <= 5:  # Mostra apenas os 5 primeiros
                print(f"   ✓ {agendamento.curso.nome} - "
                      f"{agendamento.data_inicio.strftime('%d/%m/%Y')} "
                      f"[{agendamento.get_status_display()}]")

        except Exception as e:
            # Ignora conflitos (veículo já agendado, etc)
            pass

    if agendamentos_criados > 5:
        print(f"   ... e mais {agendamentos_criados - 5} agendamentos")

    return agendamentos_criados


def imprimir_resumo():
    """Imprime resumo dos dados criados"""
    print("\n" + "=" * 60)
    print("  ✅ DADOS DE EXEMPLO CARREGADOS COM SUCESSO!")
    print("=" * 60)

    print("\n📊 Resumo:")
    print(f"  • Cursos: {Curso.objects.count()}")
    print(f"  • Veículos: {Veiculo.objects.count()}")
    print(f"  • Professores: "
          f"{Usuario.objects.filter(tipo_usuario='professor').count()}")
    print(f"  • Agendamentos: {Agendamento.objects.count()}")
    print(f"    - Pendentes: "
          f"{Agendamento.objects.filter(status='pendente').count()}")
    print(f"    - Aprovados: "
          f"{Agendamento.objects.filter(status='aprovado').count()}")
    print(f"    - Reprovados: "
          f"{Agendamento.objects.filter(status='reprovado').count()}")
    print(f"  • Trajetos: {Trajeto.objects.count()}")

    print("\n👤 Credenciais de Teste:")
    print("  ┌─ Professores:")
    for i in range(1, min(4, 11)):
        print(f"  │  • Username: prof{i:02d}  Senha: senha123")
    if Usuario.objects.filter(tipo_usuario='professor').count() > 3:
        print(f"  └─ ... (total: "
              f"{Usuario.objects.filter(tipo_usuario='professor').count()})")

    print("\n💡 Próximos Passos:")
    print("  1. python manage.py createsuperuser  (se ainda não criou)")
    print("  2. python manage.py runserver")
    print("  3. Acesse: http://127.0.0.1:8000/")

    print("\n" + "=" * 60)


def criar_dados_exemplo():
    """Função principal que coordena a criação de todos os dados"""
    print("\n" + "=" * 60)
    print("  🚀 CARREGANDO DADOS DE EXEMPLO COM FAKER")
    print("=" * 60)

    try:
        # Cria dados em sequência
        cursos = criar_cursos()
        veiculos = criar_veiculos()
        professores = criar_professores(quantidade=10)

        print("\n⏳ [5/5] Processando agendamentos e trajetos...")
        agendamentos_criados = criar_agendamentos(
            cursos, veiculos, professores, quantidade=20
        )

        # Imprime resumo
        imprimir_resumo()

    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    criar_dados_exemplo()
