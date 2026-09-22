from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Categoria, DetallePedido, Juego, Pedido, PerfilUsuario, Rol


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'descripcion')
    search_fields = ('nombre', 'codigo')


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol', 'fecha_nacimiento', 'actualizado_en')
    list_filter = ('rol',)
    search_fields = (
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
        'usuario__email',
    )
    list_select_related = ('usuario', 'rol')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'orden')
    list_editable = ('orden',)
    search_fields = ('nombre', 'slug')


@admin.register(Juego)
class JuegoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'activo')
    list_filter = ('categoria', 'activo')
    list_editable = ('precio', 'stock', 'activo')
    search_fields = ('nombre', 'descripcion')


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    can_delete = False
    readonly_fields = (
        'juego',
        'nombre_juego',
        'precio_unitario',
        'cantidad',
    )


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'usuario', 'estado', 'total', 'creado_en')
    list_filter = ('estado', 'creado_en')
    search_fields = ('codigo', 'usuario__username', 'usuario__email')
    readonly_fields = ('codigo', 'usuario', 'total', 'creado_en')
    inlines = (DetallePedidoInline,)


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    extra = 0


Usuario = get_user_model()
admin.site.unregister(Usuario)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    inlines = (PerfilUsuarioInline,)
