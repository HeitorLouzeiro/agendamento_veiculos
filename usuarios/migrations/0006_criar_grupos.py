from django.db import migrations


GRUPOS = ['Administradores', 'Professores', 'Motoristas', 'Responsaveis de Campus']

MAPA_TIPO = {
    'administrador': 'Administradores',
    'professor': 'Professores',
}


def criar_grupos_e_migrar(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Usuario = apps.get_model('usuarios', 'Usuario')

    grupos = {}
    for nome in GRUPOS:
        grupo, _ = Group.objects.get_or_create(name=nome)
        grupos[nome] = grupo

    for usuario in Usuario.objects.all():
        tipo = getattr(usuario, 'tipo_usuario', None)
        nome_grupo = MAPA_TIPO.get(tipo)
        if nome_grupo:
            usuario.groups.add(grupos[nome_grupo])


def remover_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=GRUPOS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('usuarios', '0005_add_token_ativacao'),
    ]

    operations = [
        migrations.RunPython(criar_grupos_e_migrar, remover_grupos),
    ]
