from datetime import date

from django.contrib.auth.hashers import make_password
from django.db import migrations


def crear_datos_iniciales(apps, schema_editor):
    Rol = apps.get_model('tienda', 'Rol')
    PerfilUsuario = apps.get_model('tienda', 'PerfilUsuario')
    Usuario = apps.get_model('auth', 'User')
    base_datos = schema_editor.connection.alias

    roles = {}
    definiciones_roles = (
        (
            'cliente',
            'Cliente',
            'Consulta el catálogo y administra su propio perfil.',
        ),
        (
            'administrador',
            'Administrador',
            'Accede al panel destinado a la administración de recursos.',
        ),
    )

    for codigo, nombre, descripcion in definiciones_roles:
        rol, _ = Rol.objects.using(base_datos).update_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'descripcion': descripcion,
            },
        )
        roles[codigo] = rol

    cuentas = (
        {
            'username': 'cliente',
            'password': 'Cliente#2026',
            'first_name': 'Cliente',
            'last_name': 'FreeGames',
            'email': 'cliente@freegames.cl',
            'is_staff': False,
            'is_superuser': False,
            'rol': roles['cliente'],
            'fecha_nacimiento': date(2000, 1, 1),
        },
        {
            'username': 'admin',
            'password': 'Admin#2026',
            'first_name': 'Administrador',
            'last_name': 'FreeGames',
            'email': 'admin@freegames.cl',
            'is_staff': True,
            'is_superuser': True,
            'rol': roles['administrador'],
            'fecha_nacimiento': date(1990, 1, 1),
        },
    )

    for datos in cuentas:
        usuario, _ = Usuario.objects.using(base_datos).update_or_create(
            username=datos['username'],
            defaults={
                'password': make_password(datos['password']),
                'first_name': datos['first_name'],
                'last_name': datos['last_name'],
                'email': datos['email'],
                'is_active': True,
                'is_staff': datos['is_staff'],
                'is_superuser': datos['is_superuser'],
            },
        )
        PerfilUsuario.objects.using(base_datos).update_or_create(
            usuario_id=usuario.pk,
            defaults={
                'rol': datos['rol'],
                'fecha_nacimiento': datos['fecha_nacimiento'],
                'direccion': '',
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            crear_datos_iniciales,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
