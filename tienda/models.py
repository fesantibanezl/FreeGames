from django.conf import settings
from django.db import models


class Rol(models.Model):
    """Define los dos tipos de acceso solicitados para FreeGames."""

    class Codigos(models.TextChoices):
        CLIENTE = 'cliente', 'Cliente'
        ADMINISTRADOR = 'administrador', 'Administrador'

    codigo = models.CharField(
        max_length=20,
        unique=True,
        choices=Codigos.choices,
    )
    nombre = models.CharField(max_length=40)
    descripcion = models.CharField(max_length=180, blank=True)

    class Meta:
        ordering = ('nombre',)
        verbose_name = 'rol'
        verbose_name_plural = 'roles'

    def __str__(self):
        return self.nombre


class PerfilUsuario(models.Model):
    """Extiende el usuario de Django con los datos propios de FreeGames."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        related_name='perfiles',
    )
    fecha_nacimiento = models.DateField(null=True, blank=True)
    direccion = models.CharField(max_length=160, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('usuario__username',)
        verbose_name = 'perfil de usuario'
        verbose_name_plural = 'perfiles de usuario'

    def __str__(self):
        return f'{self.usuario.username} ({self.rol.nombre})'
