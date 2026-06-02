"""
Management command para resetar o banco e recarregar dados de exemplo.

Uso:
  python manage.py reset_db                  # reseta e carrega padrões
  python manage.py reset_db --campi 5 ...    # repassa args ao load_sample_data
  python manage.py reset_db --no-seed        # só reseta, sem dados
"""
import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Reseta o banco de dados e recarrega dados de exemplo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-seed',
            action='store_true',
            help='Apenas reseta o banco sem carregar dados de exemplo',
        )
        # Repassa todos os argumentos do load_sample_data
        parser.add_argument('--campi', type=int, default=3)
        parser.add_argument('--administradores', type=int, default=3)
        parser.add_argument('--professores', type=int, default=10)
        parser.add_argument('--motoristas', type=int, default=3)
        parser.add_argument('--agendamentos', type=int, default=20)

    def handle(self, *args, **options):
        db = settings.DATABASES['default']
        engine = db['ENGINE']

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("  RESET DO BANCO DE DADOS")
        self.stdout.write("=" * 60)

        if 'sqlite3' in engine:
            self._reset_sqlite(db)
        elif 'postgresql' in engine:
            self._reset_postgresql(db)
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Engine nao suportada: {engine}"
                )
            )
            return

        self.stdout.write("\n[migrations] Aplicando migrations...")
        call_command('migrate', '--run-syncdb', verbosity=1)

        if not options['no_seed']:
            self.stdout.write("")
            call_command(
                'load_sample_data',
                campi=options['campi'],
                administradores=options['administradores'],
                professores=options['professores'],
                motoristas=options['motoristas'],
                agendamentos=options['agendamentos'],
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nBanco resetado sem dados de exemplo.')
            )

    # ------------------------------------------------------------------ #

    def _reset_sqlite(self, db):
        db_path = str(db['NAME'])
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(
                self.style.WARNING(f"[sqlite] Arquivo removido: {db_path}")
            )
        else:
            self.stdout.write(f"[sqlite] Arquivo nao encontrado, continuando.")

    def _reset_postgresql(self, db):
        from django.db import connection

        self.stdout.write(
            self.style.WARNING(
                f"[postgres] Dropando schema public em "
                f"'{db.get('NAME')}'..."
            )
        )

        with connection.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE;")
            cursor.execute("CREATE SCHEMA public;")
            cursor.execute(
                "GRANT ALL ON SCHEMA public TO PUBLIC;"
            )

        self.stdout.write(
            self.style.WARNING("[postgres] Schema recriado com sucesso.")
        )
