"""
Carrega dados fixos e previsíveis para desenvolvimento.
Uso: python manage.py create_data_load
"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils import timezone

from agendamentos.models import Agendamento, Trajeto
from campus.models import Campus
from cursos.models import Curso
from frotas.models import Abastecimento, Ocorrencia
from usuarios.models import Usuario
from veiculos.models import Veiculo


# ------------------------------------------------------------------ #
#  Dados fixos                                                         #
# ------------------------------------------------------------------ #

CAMPI = [
    {
        'nome': 'Campus Torquato Neto',
        'cidade': 'Teresina',
        'endereco': 'Rua João Cabral, 2231 - Pirajá',
    },
    {
        'nome': 'Campus Alexandre Alves de Oliveira',
        'cidade': 'Parnaíba',
        'endereco': 'Av. São Sebastião, 2819 - Nossa Senhora de Fátima',
    },
]

CURSOS = [
    # (nome, campus_index, limite_km)
    ('Engenharia Civil',          0, 800),
    ('Arquitetura e Urbanismo',   0, 900),
    ('Administração',             0, 500),
    ('Direito',                   1, 350),
    ('Enfermagem',                1, 700),
]

VEICULOS = [
    # (placa, modelo, marca, ano, cor, capacidade, campus_index)
    ('TST-0A01', 'Sprinter',  'Mercedes',  2022, 'Branco', 15, 0),
    ('TST-0B02', 'Hilux',     'Toyota',    2023, 'Prata',   5, 0),
    ('TST-0C03', 'Master',    'Renault',   2021, 'Branco', 16, 1),
]

USUARIOS = [
    # (username, senha, first, last, email, grupo, campus_index, cnh)
    ('admin',    'admin123',  'Admin',     'Principal',  'admin@uespi.br',    'Administradores',        None, ''),
    ('resp01',   'resp123',   'Carlos',    'Oliveira',   'resp01@uespi.br',   'Responsaveis de Campus', 0,    ''),
    ('resp02',   'resp123',   'Fernanda',  'Lima',       'resp02@uespi.br',   'Responsaveis de Campus', 1,    ''),
    ('prof01',   'senha123',  'Ana',       'Souza',      'prof01@uespi.br',   'Professores',            0,    ''),
    ('prof02',   'senha123',  'Bruno',     'Costa',      'prof02@uespi.br',   'Professores',            0,    ''),
    ('prof03',   'senha123',  'Carla',     'Mendes',     'prof03@uespi.br',   'Professores',            1,    ''),
    ('motor01',  'motor123',  'Diego',     'Alves',      'motor01@uespi.br',  'Motoristas',             0,    '01234567890'),
    ('motor02',  'motor123',  'Eliane',    'Rocha',      'motor02@uespi.br',  'Motoristas',             1,    '09876543210'),
]


class Command(BaseCommand):
    help = 'Cria dados fixos de desenvolvimento (sem argumentos)'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '=' * 55)
        self.stdout.write('  create_data_load')
        self.stdout.write('=' * 55)

        campi    = self._criar_campi()
        usuarios = self._criar_usuarios(campi)
        cursos   = self._criar_cursos(campi)
        veiculos = self._criar_veiculos(campi)
        self._criar_agendamentos(cursos, veiculos, usuarios)
        self._criar_abastecimentos(veiculos, usuarios)
        self._criar_ocorrencias(usuarios)

        self._resumo(campi)

    # ------------------------------------------------------------------ #

    def _criar_campi(self):
        self.stdout.write('\n[1] Campi')
        campi = []
        for d in CAMPI:
            obj, created = Campus.objects.get_or_create(
                nome=d['nome'],
                defaults={'cidade': d['cidade'], 'endereco': d['endereco'], 'ativo': True},
            )
            self._log(created, obj.nome, obj.cidade)
            campi.append(obj)
        return campi

    def _criar_usuarios(self, campi):
        self.stdout.write('\n[2] Usuários')
        grupos = {
            nome: Group.objects.get_or_create(name=nome)[0]
            for nome in [
                'Administradores', 'Responsaveis de Campus',
                'Professores', 'Motoristas',
            ]
        }

        usuarios = {}
        for (username, senha, first, last, email,
             grupo_nome, campus_idx, cnh) in USUARIOS:

            campus = campi[campus_idx] if campus_idx is not None else None
            is_admin = grupo_nome == 'Administradores'

            u, created = Usuario.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'email': email,
                    'campus': campus,
                    'numero_habilitacao': cnh,
                    'is_staff': is_admin,
                    'is_superuser': is_admin,
                },
            )
            if created:
                u.set_password(senha)
                u.save()
                u.groups.add(grupos[grupo_nome])

            label = f'{u.get_full_name()} ({username} / {senha})'
            if campus:
                label += f'  → {campus.nome}'
            self._log(created, label)
            usuarios[username] = u

        return usuarios

    def _criar_cursos(self, campi):
        self.stdout.write('\n[3] Cursos')
        cursos = []
        for nome, campus_idx, limite in CURSOS:
            campus = campi[campus_idx]
            obj, created = Curso.objects.get_or_create(
                nome=nome,
                defaults={'campus': campus, 'limite_km_mensal': limite, 'ativo': True},
            )
            self._log(created, f'{obj.nome}  ({campus.cidade}, {limite} km/mês)')
            cursos.append(obj)
        return cursos

    def _criar_veiculos(self, campi):
        self.stdout.write('\n[4] Veículos')
        veiculos = []
        for placa, modelo, marca, ano, cor, cap, campus_idx in VEICULOS:
            campus = campi[campus_idx]
            obj, created = Veiculo.objects.get_or_create(
                placa=placa,
                defaults={
                    'campus': campus, 'modelo': modelo, 'marca': marca,
                    'ano': ano, 'cor': cor, 'capacidade_passageiros': cap,
                    'ativo': True,
                },
            )
            self._log(created, f'{obj.placa} — {marca} {modelo}  ({campus.cidade})')
            veiculos.append(obj)
        return veiculos

    def _criar_agendamentos(self, cursos, veiculos, usuarios):
        self.stdout.write('\n[5] Agendamentos')
        now = timezone.now().replace(minute=0, second=0, microsecond=0)

        dados = [
            # (curso_idx, veiculo_idx, professor, delta_dias, hora, status, destino, km)
            (0, 0, 'prof01', -10,  8, 'aprovado',  'Canteiro de Obras Central', 45),
            (1, 0, 'prof01',  -3,  7, 'aprovado',  'Prefeitura Municipal',      30),
            (2, 1, 'prof02',   2,  9, 'pendente',  'Empresa de Consultoria',    20),
            (3, 2, 'prof03', -15, 13, 'aprovado',  'Fórum da Comarca',          60),
            (4, 2, 'prof03',   7,  8, 'pendente',  'Hospital Regional',         55),
            (0, 1, 'prof02',  -5,  7, 'reprovado', 'Obra Residencial',          40),
        ]

        agendamentos_criados = []
        for curso_idx, veiculo_idx, prof_key, dias, hora, status, destino, km in dados:
            inicio = (now + timedelta(days=dias)).replace(hour=hora)
            fim    = inicio + timedelta(hours=8)

            ag, created = Agendamento.objects.get_or_create(
                professor=usuarios[prof_key],
                veiculo=veiculos[veiculo_idx],
                data_inicio=inicio,
                defaults={
                    'curso': cursos[curso_idx],
                    'data_fim': fim,
                    'status': status,
                    'observacoes': f'Visita técnica — {destino}',
                    'motivo_reprovacao': (
                        'Veículo indisponível no período solicitado.'
                        if status == 'reprovado' else ''
                    ),
                },
            )
            if created:
                origem = 'Campus Universitário'
                Trajeto.objects.create(
                    agendamento=ag, origem=origem, destino=destino,
                    data_saida=inicio,
                    data_chegada=inicio + timedelta(hours=2),
                    quilometragem=km, descricao=f'Ida para {destino}',
                )
                Trajeto.objects.create(
                    agendamento=ag, origem=destino, destino=origem,
                    data_saida=inicio + timedelta(hours=5),
                    data_chegada=inicio + timedelta(hours=7),
                    quilometragem=km, descricao=f'Retorno de {destino}',
                )
            self._log(created,
                      f'{cursos[curso_idx].nome} — '
                      f'{inicio:%d/%m/%Y} [{status}]')
            agendamentos_criados.append(ag)

        return agendamentos_criados

    def _criar_abastecimentos(self, veiculos, usuarios):
        self.stdout.write('\n[6] Abastecimentos')
        now = timezone.now().replace(minute=0, second=0, microsecond=0)

        dados = [
            # (veiculo_idx, motorista, delta_dias, posto, km, litros, valor, combustivel)
            (0, 'motor01', -8,  'Posto Shell Pirajá',   12500, Decimal('45.0'), Decimal('270.00'), 'gasolina'),
            (0, 'motor01', -3,  'Posto Ipiranga Centro', 12900, Decimal('40.0'), Decimal('244.00'), 'gasolina'),
            (1, 'motor01', -6,  'Posto BR Leste',        8300, Decimal('50.0'), Decimal('280.00'), 'diesel'),
            (2, 'motor02', -12, 'Posto Ale Parnaíba',    5100, Decimal('38.0'), Decimal('220.40'), 'etanol'),
            (2, 'motor02', -2,  'Posto Shell Parnaíba',  5500, Decimal('42.0'), Decimal('252.00'), 'etanol'),
        ]

        for veiculo_idx, motor_key, dias, posto, km, litros, valor, comb in dados:
            dt = (now + timedelta(days=dias)).replace(hour=10)
            obj, created = Abastecimento.objects.get_or_create(
                veiculo=veiculos[veiculo_idx],
                motorista=usuarios[motor_key],
                data_hora=dt,
                defaults={
                    'local_posto': posto,
                    'km_atual': km,
                    'litros_abastecidos': litros,
                    'valor_gasto': valor,
                    'tipo_combustivel': comb,
                },
            )
            self._log(
                created,
                f'{veiculos[veiculo_idx].placa} — {posto} — '
                f'{litros} L / R$ {valor}',
            )

    def _criar_ocorrencias(self, usuarios):
        self.stdout.write('\n[7] Ocorrências')

        # precisa de um agendamento aprovado para vincular
        ags_aprovados = list(
            Agendamento.objects.filter(status='aprovado').select_related('veiculo')
        )
        if not ags_aprovados:
            self.stdout.write('   (nenhum agendamento aprovado disponível)')
            return

        dados = [
            # (ag_idx, motorista, tipo, gravidade, local, descricao, resolvido)
            (0, 'motor01', 'avaria',   'baixa',  'Rodovia PI-113 km 12',
             'Pneu furado durante trajeto de ida.', True),
            (1, 'motor01', 'multa',    'media',  'Av. Frei Serafim, Teresina',
             'Autuado por excesso de velocidade (72 km/h em via de 60).', False),
            (2, 'motor02', 'pane',     'alta',   'BR-343, Parnaíba',
             'Falha no sistema de arrefecimento. Veículo rebocado.', True),
        ]

        for ag_idx, motor_key, tipo, grav, local, desc, resolvido in dados:
            if ag_idx >= len(ags_aprovados):
                continue
            ag = ags_aprovados[ag_idx]
            obj, created = Ocorrencia.objects.get_or_create(
                agendamento=ag,
                tipo=tipo,
                defaults={
                    'veiculo': ag.veiculo,
                    'motorista': usuarios[motor_key],
                    'gravidade': grav,
                    'data_hora': ag.data_inicio + timedelta(hours=3),
                    'local': local,
                    'descricao': desc,
                    'resolvido': resolvido,
                },
            )
            self._log(created, f'[{tipo}] {grav} — {local}')

    # ------------------------------------------------------------------ #

    def _log(self, created, *parts):
        line = '  ' + ('✓' if created else '→') + '  ' + '  '.join(str(p) for p in parts)
        if not created:
            line += '  (já existe)'
        self.stdout.write(line)

    def _resumo(self, campi):
        self.stdout.write('\n' + '=' * 55)

        linhas = [
            ('Campi',          Campus.objects.count()),
            ('Usuários',       Usuario.objects.count()),
            ('  Admins',       Usuario.objects.filter(groups__name='Administradores').count()),
            ('  Responsáveis', Usuario.objects.filter(groups__name='Responsaveis de Campus').count()),
            ('  Professores',  Usuario.objects.filter(groups__name='Professores').count()),
            ('  Motoristas',   Usuario.objects.filter(groups__name='Motoristas').count()),
            ('Cursos',         Curso.objects.count()),
            ('Veículos',       Veiculo.objects.count()),
            ('Agendamentos',   Agendamento.objects.count()),
            ('Trajetos',       Trajeto.objects.count()),
            ('Abastecimentos', Abastecimento.objects.count()),
            ('Ocorrências',    Ocorrencia.objects.count()),
        ]
        for label, count in linhas:
            self.stdout.write(f'  {label:<16} {count}')

        self.stdout.write('\n  Credenciais:')
        for username, senha, *_ in USUARIOS:
            u = Usuario.objects.get(username=username)
            campus_str = f' ({u.campus.nome})' if u.campus else ''
            grupo = u.groups.first()
            grupo_str = grupo.name if grupo else ''
            self.stdout.write(
                f'    {username:<10} / {senha:<10}  {grupo_str}{campus_str}'
            )

        self.stdout.write('=' * 55 + '\n')
