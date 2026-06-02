"""
Management command para carregar dados de exemplo no sistema
Uso: python manage.py load_sample_data
"""
import random
from datetime import timedelta

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from agendamentos.models import Agendamento, Trajeto
from campus.models import Campus
from cursos.models import Curso
from usuarios.models import Usuario
from veiculos.models import Veiculo


CAMPI_DATA = [
    {
        'nome': 'Campus Torquato Neto',
        'cidade': 'Teresina',
        'endereco': 'Rua João Cabral, 2231 - Pirajá',
    },
    {
        'nome': 'Campus Clóvis Moura',
        'cidade': 'Teresina',
        'endereco': 'Av. Pedro Freitas, s/n - São Pedro',
    },
    {
        'nome': 'Campus Alexandre Alves de Oliveira',
        'cidade': 'Parnaíba',
        'endereco': 'Av. São Sebastião, 2819 - Nossa Senhora de Fátima',
    },
    {
        'nome': 'Campus Heróis do Jenipapo',
        'cidade': 'Campo Maior',
        'endereco': 'Av. Deputado Pinheiro Nogueira, 800',
    },
    {
        'nome': 'Campus Senador Helvídio Nunes de Barros',
        'cidade': 'Picos',
        'endereco': 'Rua Cícero Eduardo, s/n - Junco',
    },
]

CURSOS_POR_CAMPUS = [
    {'nome': 'Engenharia Mecânica', 'limite_km_mensal': 1000,
     'descricao': 'Atividades práticas e visitas técnicas'},
    {'nome': 'Engenharia Civil', 'limite_km_mensal': 800,
     'descricao': 'Visitas a obras e canteiros'},
    {'nome': 'Engenharia Elétrica', 'limite_km_mensal': 600,
     'descricao': 'Visitas a usinas e subestações'},
    {'nome': 'Arquitetura e Urbanismo', 'limite_km_mensal': 900,
     'descricao': 'Estudos de campo e visitas arquitetônicas'},
    {'nome': 'Administração', 'limite_km_mensal': 500,
     'descricao': 'Visitas empresariais e eventos'},
    {'nome': 'Ciências Contábeis', 'limite_km_mensal': 400,
     'descricao': 'Visitas a empresas e auditoria'},
    {'nome': 'Direito', 'limite_km_mensal': 350,
     'descricao': 'Visitas a fóruns e tribunais'},
    {'nome': 'Enfermagem', 'limite_km_mensal': 700,
     'descricao': 'Visitas a unidades de saúde'},
    {'nome': 'Medicina Veterinária', 'limite_km_mensal': 800,
     'descricao': 'Visitas a fazendas e clínicas'},
    {'nome': 'Agronomia', 'limite_km_mensal': 1200,
     'descricao': 'Visitas a propriedades rurais'},
]

VEICULOS_DATA = [
    {'placa': 'ABC-1A34', 'modelo': 'Sprinter',
     'marca': 'Mercedes', 'ano': 2022, 'cor': 'Branco',
     'capacidade': 15, 'obs': 'Van para transporte de grupos'},
    {'placa': 'XYZ-2B78', 'modelo': 'Hilux',
     'marca': 'Toyota', 'ano': 2023, 'cor': 'Prata',
     'capacidade': 5, 'obs': 'Caminhonete para trabalhos de campo'},
    {'placa': 'DEF-3C12', 'modelo': 'Ducato',
     'marca': 'Fiat', 'ano': 2021, 'cor': 'Branco',
     'capacidade': 16, 'obs': 'Van para viagens longas'},
    {'placa': 'GHI-4D56', 'modelo': 'Daily',
     'marca': 'Iveco', 'ano': 2020, 'cor': 'Branco',
     'capacidade': 16, 'obs': 'Micro-ônibus para grupos'},
    {'placa': 'JKL-5E90', 'modelo': 'Master',
     'marca': 'Renault', 'ano': 2020, 'cor': 'Cinza',
     'capacidade': 16, 'obs': 'Van para eventos'},
    {'placa': 'MNO-6F23', 'modelo': 'Transit',
     'marca': 'Ford', 'ano': 2022, 'cor': 'Branco',
     'capacidade': 15, 'obs': 'Van universitária'},
    {'placa': 'PQR-7G67', 'modelo': 'Boxer',
     'marca': 'Peugeot', 'ano': 2019, 'cor': 'Branco',
     'capacidade': 16, 'obs': 'Van para viagens'},
    {'placa': 'STU-8H01', 'modelo': 'Jumper',
     'marca': 'Citroën', 'ano': 2021, 'cor': 'Branco',
     'capacidade': 16, 'obs': 'Van para transporte'},
    {'placa': 'VWX-9I45', 'modelo': 'Vito',
     'marca': 'Mercedes', 'ano': 2023, 'cor': 'Prata',
     'capacidade': 8, 'obs': 'Van executiva'},
    {'placa': 'YZA-0J89', 'modelo': 'Spin',
     'marca': 'Chevrolet', 'ano': 2022, 'cor': 'Branco',
     'capacidade': 7, 'obs': 'Veículo para pequenos grupos'},
]

PERGUNTAS_RESPOSTAS = [
    ('cidade_nascimento', 'Teresina'),
    ('nome_mae', 'Maria Silva'),
    ('animal_estimacao', 'Rex'),
    ('escola', 'Escola Estadual'),
    ('comida_favorita', 'Pizza'),
    ('time', 'Flamengo'),
    ('livro_favorito', 'Dom Casmurro'),
    ('professor_favorito', 'Professor João'),
]


class Command(BaseCommand):
    help = 'Carrega dados de exemplo no sistema usando Faker'

    def add_arguments(self, parser):
        parser.add_argument(
            '--campi',
            type=int,
            default=3,
            help='Quantidade de campi a criar, máx 5 (padrão: 3)'
        )
        parser.add_argument(
            '--professores',
            type=int,
            default=10,
            help='Quantidade de professores por campus (padrão: 10)'
        )
        parser.add_argument(
            '--motoristas',
            type=int,
            default=3,
            help='Quantidade de motoristas por campus (padrão: 3)'
        )
        parser.add_argument(
            '--agendamentos',
            type=int,
            default=20,
            help='Quantidade de agendamentos a criar (padrão: 20)'
        )
        parser.add_argument(
            '--administradores',
            type=int,
            default=3,
            help='Quantidade de administradores (padrão: 3, máx 3)'
        )

    def handle(self, *args, **options):
        self.fake = Faker('pt_BR')

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS("  CARREGANDO DADOS DE EXEMPLO COM FAKER")
        )
        self.stdout.write("=" * 60)

        try:
            n_campi = min(options['campi'], len(CAMPI_DATA))

            campi = self.criar_campi(n_campi)
            self.criar_administradores(options['administradores'])
            self.criar_responsaveis(campi)
            cursos = self.criar_cursos(campi)
            veiculos = self.criar_veiculos(campi)
            professores = self.criar_professores(campi, options['professores'])
            self.criar_motoristas(campi, options['motoristas'])
            self.criar_agendamentos(cursos, veiculos, professores,
                                    options['agendamentos'])

            self.imprimir_resumo(campi)

            self.stdout.write(
                self.style.SUCCESS('\nDados carregados com sucesso!')
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nERRO: {str(e)}'))
            import traceback
            traceback.print_exc()

    # ------------------------------------------------------------------ #
    #  Campi                                                               #
    # ------------------------------------------------------------------ #

    def criar_campi(self, quantidade):
        self.stdout.write(
            f"\n[1/8] Criando {quantidade} campi..."
        )
        grupo_resp, _ = Group.objects.get_or_create(
            name='Responsaveis de Campus'
        )

        campi_criados = []
        for dados in CAMPI_DATA[:quantidade]:
            campus, created = Campus.objects.get_or_create(
                nome=dados['nome'],
                defaults={
                    'cidade': dados['cidade'],
                    'endereco': dados['endereco'],
                    'ativo': True,
                }
            )
            status = 'criado' if created else 'ja existe'
            self.stdout.write(
                f"   {'✓' if created else '→'} "
                f"{campus.nome} — {campus.cidade}  [{status}]"
            )
            campi_criados.append(campus)

        return campi_criados

    # ------------------------------------------------------------------ #
    #  Administradores                                                     #
    # ------------------------------------------------------------------ #

    def criar_administradores(self, quantidade=3):
        self.stdout.write(
            f"\n[2/8] Criando {quantidade} administradores..."
        )
        grupo_admin, _ = Group.objects.get_or_create(name='Administradores')

        admins_data = [
            {
                'username': 'admin',
                'email': 'admin@uespi.br',
                'first_name': 'Admin',
                'last_name': 'Principal',
                'telefone': '(86) 99999-0001',
            },
            {
                'username': 'admin2',
                'email': 'admin2@uespi.br',
                'first_name': 'Admin',
                'last_name': 'Secundário',
                'telefone': '(86) 99999-0002',
            },
            {
                'username': 'admin3',
                'email': 'admin3@uespi.br',
                'first_name': 'Admin',
                'last_name': 'Sistema',
                'telefone': '(86) 99999-0003',
            },
        ]

        for dados in admins_data[:min(quantidade, len(admins_data))]:
            perguntas = random.sample(PERGUNTAS_RESPOSTAS, 2)
            usuario, created = Usuario.objects.get_or_create(
                username=dados['username'],
                defaults={
                    'email': dados['email'],
                    'first_name': dados['first_name'],
                    'last_name': dados['last_name'],
                    'telefone': dados['telefone'],
                    'pergunta_seguranca_1': perguntas[0][0],
                    'resposta_seguranca_1': perguntas[0][1],
                    'pergunta_seguranca_2': perguntas[1][0],
                    'resposta_seguranca_2': perguntas[1][1],
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
            if created:
                usuario.set_password('admin123')
                usuario.save()
                usuario.groups.add(grupo_admin)
                self.stdout.write(
                    f"   ✓ {usuario.get_full_name()} "
                    f"(user: {dados['username']} / senha: admin123)"
                )
            else:
                self.stdout.write(
                    f"   → {dados['username']} (ja existe)"
                )

    # ------------------------------------------------------------------ #
    #  Responsáveis de Campus                                              #
    # ------------------------------------------------------------------ #

    def criar_responsaveis(self, campi):
        self.stdout.write(
            f"\n[3/8] Criando {len(campi)} responsaveis de campus..."
        )
        grupo, _ = Group.objects.get_or_create(name='Responsaveis de Campus')

        responsaveis = []
        for i, campus in enumerate(campi, start=1):
            username = f"resp{i:02d}"
            perguntas = random.sample(PERGUNTAS_RESPOSTAS, 2)
            usuario, created = Usuario.objects.get_or_create(
                username=username,
                defaults={
                    'email': f"resp{i:02d}@uespi.br",
                    'first_name': self.fake.first_name(),
                    'last_name': self.fake.last_name(),
                    'telefone': self.fake.phone_number(),
                    'campus': campus,
                    'pergunta_seguranca_1': perguntas[0][0],
                    'resposta_seguranca_1': perguntas[0][1],
                    'pergunta_seguranca_2': perguntas[1][0],
                    'resposta_seguranca_2': perguntas[1][1],
                }
            )
            if created:
                usuario.set_password('resp123')
                usuario.save()
                usuario.groups.add(grupo)
                self.stdout.write(
                    f"   ✓ {usuario.get_full_name()} "
                    f"→ {campus.nome}  "
                    f"(user: {username} / senha: resp123)"
                )
            else:
                self.stdout.write(
                    f"   → {username} (ja existe)"
                )
            responsaveis.append(usuario)

        return responsaveis

    # ------------------------------------------------------------------ #
    #  Cursos                                                              #
    # ------------------------------------------------------------------ #

    def criar_cursos(self, campi):
        self.stdout.write("\n[4/8] Criando cursos por campus...")

        # Distribui os cursos ciclicamente entre os campi
        cursos_criados = []
        for idx, dados in enumerate(CURSOS_POR_CAMPUS):
            campus = campi[idx % len(campi)]
            nome_completo = f"{dados['nome']} — {campus.nome}"
            curso, created = Curso.objects.get_or_create(
                nome=nome_completo,
                defaults={
                    'campus': campus,
                    'limite_km_mensal': dados['limite_km_mensal'],
                    'descricao': dados['descricao'],
                    'ativo': True,
                }
            )
            if created:
                self.stdout.write(
                    f"   ✓ {dados['nome']} "
                    f"({campus.cidade}, {dados['limite_km_mensal']} km/mês)"
                )
            else:
                self.stdout.write(f"   → {nome_completo} (ja existe)")
            cursos_criados.append(curso)

        return cursos_criados

    # ------------------------------------------------------------------ #
    #  Veículos                                                            #
    # ------------------------------------------------------------------ #

    def criar_veiculos(self, campi):
        self.stdout.write("\n[5/8] Criando veiculos por campus...")

        # Distribui os veículos ciclicamente entre os campi
        veiculos_criados = []
        for idx, v_data in enumerate(VEICULOS_DATA):
            campus = campi[idx % len(campi)]
            veiculo, created = Veiculo.objects.get_or_create(
                placa=v_data['placa'],
                defaults={
                    'campus': campus,
                    'modelo': v_data['modelo'],
                    'marca': v_data['marca'],
                    'ano': v_data['ano'],
                    'cor': v_data['cor'],
                    'capacidade_passageiros': v_data['capacidade'],
                    'observacoes': v_data['obs'],
                    'ativo': True,
                }
            )
            if created:
                self.stdout.write(
                    f"   ✓ {veiculo.placa} — "
                    f"{veiculo.marca} {veiculo.modelo} "
                    f"({campus.cidade})"
                )
            else:
                self.stdout.write(f"   → {v_data['placa']} (ja existe)")
            veiculos_criados.append(veiculo)

        return veiculos_criados

    # ------------------------------------------------------------------ #
    #  Professores                                                         #
    # ------------------------------------------------------------------ #

    def criar_professores(self, campi, quantidade_por_campus=10):
        total = quantidade_por_campus * len(campi)
        self.stdout.write(
            f"\n[6/8] Criando {total} professores "
            f"({quantidade_por_campus} por campus)..."
        )
        grupo, _ = Group.objects.get_or_create(name='Professores')

        professores_criados = []
        contador = 1
        for campus in campi:
            for _ in range(quantidade_por_campus):
                username = f"prof{contador:02d}"
                perguntas = random.sample(PERGUNTAS_RESPOSTAS, 2)
                professor, created = Usuario.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f'{username}@uespi.br',
                        'first_name': self.fake.first_name(),
                        'last_name': self.fake.last_name(),
                        'telefone': self.fake.phone_number(),
                        'campus': campus,
                        'pergunta_seguranca_1': perguntas[0][0],
                        'resposta_seguranca_1': perguntas[0][1],
                        'pergunta_seguranca_2': perguntas[1][0],
                        'resposta_seguranca_2': perguntas[1][1],
                    }
                )
                if created:
                    professor.set_password('senha123')
                    professor.save()
                    professor.groups.add(grupo)
                    if contador <= 5:
                        self.stdout.write(
                            f"   ✓ {professor.get_full_name()} "
                            f"→ {campus.nome}  "
                            f"(user: {username} / senha: senha123)"
                        )
                professores_criados.append(professor)
                contador += 1

        if total > 5:
            self.stdout.write(
                f"   ... e mais {total - 5} professores criados"
            )
        return professores_criados

    # ------------------------------------------------------------------ #
    #  Motoristas                                                          #
    # ------------------------------------------------------------------ #

    def criar_motoristas(self, campi, quantidade_por_campus=3):
        total = quantidade_por_campus * len(campi)
        self.stdout.write(
            f"\n[7/8] Criando {total} motoristas "
            f"({quantidade_por_campus} por campus)..."
        )
        grupo, _ = Group.objects.get_or_create(name='Motoristas')

        contador = 1
        for campus in campi:
            for _ in range(quantidade_por_campus):
                username = f"motor{contador:02d}"
                perguntas = random.sample(PERGUNTAS_RESPOSTAS, 2)
                motorista, created = Usuario.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f'{username}@uespi.br',
                        'first_name': self.fake.first_name(),
                        'last_name': self.fake.last_name(),
                        'telefone': self.fake.phone_number(),
                        'campus': campus,
                        'numero_habilitacao': self.fake.numerify(
                            '##########'
                        ),
                        'pergunta_seguranca_1': perguntas[0][0],
                        'resposta_seguranca_1': perguntas[0][1],
                        'pergunta_seguranca_2': perguntas[1][0],
                        'resposta_seguranca_2': perguntas[1][1],
                    }
                )
                if created:
                    motorista.set_password('motor123')
                    motorista.save()
                    motorista.groups.add(grupo)
                    self.stdout.write(
                        f"   ✓ {motorista.get_full_name()} "
                        f"→ {campus.nome}  "
                        f"(user: {username} / senha: motor123)"
                    )
                else:
                    self.stdout.write(
                        f"   → {username} (ja existe)"
                    )
                contador += 1

    # ------------------------------------------------------------------ #
    #  Agendamentos                                                        #
    # ------------------------------------------------------------------ #

    def criar_agendamentos(self, cursos, veiculos, professores, quantidade=20):
        self.stdout.write(
            f"\n[8/8] Criando {quantidade} agendamentos..."
        )

        locais_origem = [
            'Campus Universitário', 'Centro de Pesquisa',
            'Laboratório Central', 'Faculdade de Engenharia',
        ]
        locais_destino = (
            [f"Empresa {self.fake.company()}" for _ in range(10)]
            + [
                'Usina Hidrelétrica', 'Canteiro de Obras',
                'Parque Industrial', 'Hospital Regional',
                'Fórum da Comarca',
            ]
        )

        status_opcoes = ['pendente', 'aprovado', 'reprovado']
        criados = 0

        for _ in range(quantidade):
            dias = random.randint(-30, 60)
            data_base = timezone.now() + timedelta(days=dias)
            hora_inicio = random.choice([7, 8, 9, 13, 14])
            hora_fim = hora_inicio + random.randint(4, 9)

            data_inicio = data_base.replace(
                hour=hora_inicio, minute=0, second=0, microsecond=0
            )
            data_fim = data_base.replace(
                hour=min(hora_fim, 23), minute=0, second=0, microsecond=0
            )

            # Prefere curso e veículo do mesmo campus que o professor
            professor = random.choice(professores)
            campus_prof = professor.campus

            cursos_campus = [
                c for c in cursos if c.campus == campus_prof
            ] or cursos
            veiculos_campus = [
                v for v in veiculos if v.campus == campus_prof
            ] or veiculos

            curso = random.choice(cursos_campus)
            veiculo = random.choice(veiculos_campus)
            status = random.choices(
                status_opcoes, weights=[3, 5, 2], k=1
            )[0]

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
                        self.fake.sentence(nb_words=12)
                        if status == 'reprovado' else ''
                    ),
                )

                km = random.randint(15, 150)
                origem = random.choice(locais_origem)
                destino = random.choice(locais_destino)

                Trajeto.objects.create(
                    agendamento=agendamento,
                    origem=origem,
                    destino=destino,
                    data_saida=data_inicio,
                    data_chegada=data_inicio + timedelta(
                        hours=random.randint(2, 4)
                    ),
                    quilometragem=km,
                    descricao=f"Ida para {destino}",
                )

                hora_retorno = data_inicio + timedelta(
                    hours=random.randint(5, 8)
                )
                Trajeto.objects.create(
                    agendamento=agendamento,
                    origem=destino,
                    destino=origem,
                    data_saida=hora_retorno,
                    data_chegada=min(
                        hora_retorno + timedelta(hours=random.randint(2, 4)),
                        data_fim,
                    ),
                    quilometragem=km,
                    descricao=f"Retorno de {destino}",
                )

                criados += 1
                if criados <= 5:
                    self.stdout.write(
                        f"   ✓ {agendamento.curso.nome[:30]} — "
                        f"{agendamento.data_inicio.strftime('%d/%m/%Y')} "
                        f"[{agendamento.get_status_display()}]"
                    )

            except Exception:
                pass

        if criados > 5:
            self.stdout.write(
                f"   ... e mais {criados - 5} agendamentos"
            )
        return criados

    # ------------------------------------------------------------------ #
    #  Resumo                                                              #
    # ------------------------------------------------------------------ #

    def imprimir_resumo(self, campi):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS("  DADOS DE EXEMPLO CARREGADOS COM SUCESSO!")
        )
        self.stdout.write("=" * 60)

        self.stdout.write("\nResumo:")
        self.stdout.write(f"  • Campi:          {Campus.objects.count()}")
        self.stdout.write(
            f"  • Administradores:"
            f" {Usuario.objects.filter(groups__name='Administradores').count()}"
        )
        self.stdout.write(
            f"  • Responsaveis:   "
            f"{Usuario.objects.filter(groups__name='Responsaveis de Campus').count()}"
        )
        self.stdout.write(f"  • Cursos:         {Curso.objects.count()}")
        self.stdout.write(f"  • Veiculos:       {Veiculo.objects.count()}")
        self.stdout.write(
            f"  • Professores:    "
            f"{Usuario.objects.filter(groups__name='Professores').count()}"
        )
        self.stdout.write(
            f"  • Motoristas:     "
            f"{Usuario.objects.filter(groups__name='Motoristas').count()}"
        )
        self.stdout.write(
            f"  • Agendamentos:   {Agendamento.objects.count()} "
            f"(pendentes: "
            f"{Agendamento.objects.filter(status='pendente').count()}, "
            f"aprovados: "
            f"{Agendamento.objects.filter(status='aprovado').count()}, "
            f"reprovados: "
            f"{Agendamento.objects.filter(status='reprovado').count()})"
        )
        self.stdout.write(f"  • Trajetos:       {Trajeto.objects.count()}")

        self.stdout.write("\nCredenciais de Teste:")
        self.stdout.write(
            "  Administrador  →  admin / admin123"
        )
        self.stdout.write(
            "  Responsavel    →  resp01 / resp123  "
            f"(campus: {campi[0].nome if campi else '-'})"
        )
        self.stdout.write(
            "  Professor      →  prof01 / senha123"
        )
        self.stdout.write(
            "  Motorista      →  motor01 / motor123"
        )

        self.stdout.write("\nCampi criados:")
        for campus in campi:
            n_resp = campus.usuarios.filter(
                groups__name='Responsaveis de Campus'
            ).count()
            n_prof = campus.usuarios.filter(
                groups__name='Professores'
            ).count()
            n_motor = campus.usuarios.filter(
                groups__name='Motoristas'
            ).count()
            n_veic = campus.veiculos.count()
            n_cursos = campus.cursos.count()
            self.stdout.write(
                f"  {campus.nome} ({campus.cidade}): "
                f"{n_resp} resp, {n_prof} prof, "
                f"{n_motor} motor, {n_veic} veic, {n_cursos} cursos"
            )

        self.stdout.write(
            "\nProximos Passos:"
        )
        self.stdout.write("  1. python manage.py runserver")
        self.stdout.write("  2. Acesse: http://127.0.0.1:8000/")
        self.stdout.write("=" * 60)
