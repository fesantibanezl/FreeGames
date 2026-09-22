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


class Categoria(models.Model):
    """Agrupa los juegos que se muestran en el catálogo."""

    slug = models.SlugField(max_length=30, unique=True)
    nombre = models.CharField(max_length=40, unique=True)
    icono = models.CharField(max_length=8)
    clase_css = models.CharField(max_length=40)
    resumen = models.CharField(max_length=100)
    descripcion_meta = models.CharField(max_length=160)
    imagen = models.CharField(max_length=160)
    imagen_alt = models.CharField(max_length=180)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ('orden', 'nombre')
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'

    def __str__(self):
        return self.nombre


class Juego(models.Model):
    """Representa un videojuego administrable y persistente."""

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='juegos',
    )
    slug = models.SlugField(max_length=80, unique=True)
    nombre = models.CharField(max_length=60, unique=True)
    descripcion = models.CharField(max_length=220)
    precio = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    imagen = models.CharField(max_length=160)
    imagen_alt = models.CharField(max_length=180)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('categoria__orden', 'nombre')
        verbose_name = 'juego'
        verbose_name_plural = 'juegos'

    @property
    def gratis(self):
        return self.precio == 0

    @property
    def precio_texto(self):
        if self.gratis:
            return 'Gratis'
        return f'${self.precio:,}'.replace(',', '.')

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    """Guarda una compra simulada realizada por un cliente."""

    class Estados(models.TextChoices):
        CONFIRMADO = 'confirmado', 'Confirmado'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='pedidos',
    )
    codigo = models.CharField(max_length=24, unique=True)
    estado = models.CharField(
        max_length=20,
        choices=Estados.choices,
        default=Estados.CONFIRMADO,
    )
    total = models.PositiveIntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-creado_en',)
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'

    @property
    def total_texto(self):
        if self.total == 0:
            return 'Gratis'
        return f'${self.total:,}'.replace(',', '.')

    def __str__(self):
        return self.codigo


class DetallePedido(models.Model):
    """Conserva los productos y valores incluidos en un pedido."""

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles',
    )
    juego = models.ForeignKey(
        Juego,
        on_delete=models.PROTECT,
        related_name='detalles_pedido',
    )
    nombre_juego = models.CharField(max_length=60)
    precio_unitario = models.PositiveIntegerField()
    cantidad = models.PositiveIntegerField()

    class Meta:
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=('pedido', 'juego'),
                name='detalle_pedido_juego_unico',
            ),
        )
        verbose_name = 'detalle de pedido'
        verbose_name_plural = 'detalles de pedido'

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad

    @property
    def subtotal_texto(self):
        if self.subtotal == 0:
            return 'Gratis'
        return f'${self.subtotal:,}'.replace(',', '.')

    def __str__(self):
        return f'{self.pedido.codigo}: {self.nombre_juego}'
