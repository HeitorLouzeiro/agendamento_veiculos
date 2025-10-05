"""
Management command para carregar dados de exemplo no sistema
Uso: python manage.py load_sample_data
"""
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from agendamentos.models import Agendamento, Trajeto
from cursos.models import Curso
from usuarios.models import Usuario
from veiculos.models import Veiculo


class Command(BaseCommand):
    help = 'Carrega dados de exemplo no sistema usando Faker'

    def add_arguments(self, parser):
        parser.add_argument(
            '--professores',
            type=int,
            default=10,
            help='Quantidade de professores a criar (padrão: 10)'
        )
        parser.add_argument(
            '--agendamentos',
            type=int,
            default=20,
            help='Quantidade de agendamentos a criar (padrão: 20)'
        )

    def handle(self, *args, **options):
        """Método principal do comando"""
        self.fake = Faker('pt_BR')
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                "  🚀 CARREGANDO DADOS DE EXEMPLO COM FAKER"
            )
        )
        self.stdout.write("=" * 60)

        try:
            # Cria dados em sequência
            cursos = self.criar_cursos()
            veiculos = self.criar_veiculos()
            professores = self.criar_professores(
                quantidade=options['professores']
            )

            self.stdout.write("\n⏳ [5/5] Processando agendamentos...")
            agendamentos_criados = self.criar_agendamentos(
                cursos, veiculos, professores,
                quantidade=options['agendamentos']
            )

            # Imprime resumo
            self.imprimir_resumo()

            self.stdout.write(
                self.style.SUCCESS('\n✅ Dados carregados com sucesso!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ ERRO: {str(e)}')
            )
            import traceback
            traceback.print_exc()
            return

    def criar_cursos(self):
        """Cria cursos de exemplo"""
        self.stdout.write("\n📚 [1/5] Criando cursos...")

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
                self.stdout.write(
                    f"   ✓ {curso.nome} "
                    f"(Limite: {curso.limite_km_mensal}km)"
                )
            else:
                self.stdout.write(f"   → {curso.nome} (já existe)")
            cursos_criados.append(curso)

        return cursos_criados

    def criar_veiculos(self):
        """Cria veículos de exemplo"""
        self.stdout.write("\n🚗 [2/5] Criando veículos...")

        veiculos_data = [
            {
                'placa': 'ABC-1234', 'modelo': 'Sprinter',
                'marca': 'Mercedes', 'ano': 2022, 'cor': 'Branco',
                'capacidade': 15, 'obs': 'Van para transporte de grupos'
            },
            {
                'placa': 'XYZ-5678', 'modelo': 'Hilux',
                'marca': 'Toyota', 'ano': 2023, 'cor': 'Prata',
                'capacidade': 5, 'obs': 'Caminhonete para trabalhos'
            },
            {
                'placa': 'DEF-9012', 'modelo': 'Ducato',
                'marca': 'Fiat', 'ano': 2021, 'cor': 'Branco',
                'capacidade': 16, 'obs': 'Van para viagens longas'
            },
            {
                'placa': 'GHI-3456', 'modelo': 'Kombi',
                'marca': 'Volkswagen', 'ano': 2014, 'cor': 'Branco',
                'capacidade': 9, 'obs': 'Transporte pequenos grupos'
            },
            {
                'placa': 'JKL-7890', 'modelo': 'Master',
                'marca': 'Renault', 'ano': 2020, 'cor': 'Cinza',
                'capacidade': 16, 'obs': 'Van para eventos'
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
                self.stdout.write(
                    f"   ✓ {veiculo.placa} - {veiculo.marca} "
                    f"{veiculo.modelo} "
                    f"({veiculo.capacidade_passageiros} passageiros)"
                )
            else:
                self.stdout.write(f"   → {veiculo.placa} (já existe)")
            veiculos_criados.append(veiculo)

        return veiculos_criados

    def criar_professores(self, quantidade=10):
        """Cria professores com dados realistas"""
        self.stdout.write(
            f"\n👨‍🏫 [3/5] Criando {quantidade} professores..."
        )

        professores_criados = []
        for i in range(quantidade):
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            username = f"prof{i+1:02d}"

            professor, created = Usuario.objects.get_or_create(
                username=username,
                defaults={
                    'email': self.fake.email(),
                    'first_name': first_name,
                    'last_name': last_name,
                    'tipo_usuario': 'professor',
                    'telefone': self.fake.phone_number()
                }
            )

            if created:
                professor.set_password('senha123')
                professor.save()
                self.stdout.write(
                    f"   ✓ {professor.get_full_name()} "
                    f"(user: {username}, senha: senha123)"
                )
            professores_criados.append(professor)

        return professores_criados

    def criar_agendamentos(self, cursos, veiculos,
                           professores, quantidade=20):
        """Cria agendamentos realistas com trajetos"""
        self.stdout.write(
            f"\n📅 [4/5] Criando {quantidade} agendamentos..."
        )

        # Locais comuns
        locais_origem = [
            'Campus Universitário', 'Centro de Pesquisa',
            'Laboratório Central', 'Faculdade de Engenharia'
        ]

        locais_destino = [
            f"Empresa {self.fake.company()}" for _ in range(15)
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
            # Gera data aleatória (timezone-aware)
            dias = random.randint(-30, 60)
            data_base = timezone.now() + timedelta(days=dias)

            # Horários realistas
            hora_inicio = random.choice([7, 8, 9, 13, 14])
            hora_fim = hora_inicio + random.randint(4, 9)

            data_inicio = data_base.replace(
                hour=hora_inicio, minute=0, second=0, microsecond=0
            )
            data_fim = data_base.replace(
                hour=min(hora_fim, 23), minute=0,
                second=0, microsecond=0
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
                    observacoes=self.fake.sentence(nb_words=10),
                    motivo_reprovacao=(
                        self.fake.sentence(nb_words=15)
                        if status == 'reprovado' else ''
                    )
                )

                # Cria trajetos
                origem = random.choice(locais_origem)
                destino = random.choice(locais_destino)
                km = random.randint(15, 100)

                # Ida
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

                # Volta
                hora_saida_volta = hora_chegada_ida + timedelta(
                    hours=random.randint(2, 5)
                )
                hora_chegada_volta = min(
                    hora_saida_volta + timedelta(
                        hours=random.randint(2, 4)
                    ),
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
                if agendamentos_criados <= 5:
                    self.stdout.write(
                        f"   ✓ {agendamento.curso.nome} - "
                        f"{agendamento.data_inicio.strftime('%d/%m/%Y')} "
                        f"[{agendamento.get_status_display()}]"
                    )

            except Exception:
                # Ignora conflitos
                pass

        if agendamentos_criados > 5:
            self.stdout.write(
                f"   ... e mais {agendamentos_criados - 5} "
                f"agendamentos"
            )

        return agendamentos_criados

    def imprimir_resumo(self):
        """Imprime resumo dos dados criados"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                "  ✅ DADOS DE EXEMPLO CARREGADOS COM SUCESSO!"
            )
        )
        self.stdout.write("=" * 60)

        self.stdout.write("\n📊 Resumo:")
        self.stdout.write(f"  • Cursos: {Curso.objects.count()}")
        self.stdout.write(f"  • Veículos: {Veiculo.objects.count()}")
        self.stdout.write(
            f"  • Professores: "
            f"{Usuario.objects.filter(tipo_usuario='professor').count()}"
        )
        self.stdout.write(
            f"  • Agendamentos: {Agendamento.objects.count()}"
        )
        self.stdout.write(
            f"    - Pendentes: "
            f"{Agendamento.objects.filter(status='pendente').count()}"
        )
        self.stdout.write(
            f"    - Aprovados: "
            f"{Agendamento.objects.filter(status='aprovado').count()}"
        )
        self.stdout.write(
            f"    - Reprovados: "
            f"{Agendamento.objects.filter(status='reprovado').count()}"
        )
        self.stdout.write(f"  • Trajetos: {Trajeto.objects.count()}")

        self.stdout.write("\n👤 Credenciais de Teste:")
        self.stdout.write("  ┌─ Professores:")
        for i in range(1, min(4, 11)):
            self.stdout.write(
                f"  │  • Username: prof{i:02d}  Senha: senha123"
            )
        prof_count = Usuario.objects.filter(
            tipo_usuario='professor'
        ).count()
        if prof_count > 3:
            self.stdout.write(f"  └─ ... (total: {prof_count})")

        self.stdout.write("\n💡 Próximos Passos:")
        self.stdout.write(
            "  1. python manage.py createsuperuser  "
            "(se ainda não criou)"
        )
        self.stdout.write("  2. python manage.py runserver")
        self.stdout.write("  3. Acesse: http://127.0.0.1:8000/")

        self.stdout.write("\n" + "=" * 60)
