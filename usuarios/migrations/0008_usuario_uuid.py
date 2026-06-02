import uuid

from django.db import migrations, models


def gerar_uuids(apps, schema_editor):
    Usuario = apps.get_model('usuarios', 'Usuario')
    for usuario in Usuario.objects.all():
        usuario.uuid = uuid.uuid4()
        usuario.save(update_fields=['uuid'])


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0007_remove_tipo_usuario_add_campus'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='UUID'),
        ),
        migrations.RunPython(gerar_uuids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='usuario',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID'),
        ),
    ]
