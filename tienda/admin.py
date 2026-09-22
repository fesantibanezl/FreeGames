from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import PerfilUsuario, Rol


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


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    extra = 0


Usuario = get_user_model()
admin.site.unregister(Usuario)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    inlines = (PerfilUsuarioInline,)
