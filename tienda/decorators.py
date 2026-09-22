from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import PerfilUsuario, Rol


def obtener_codigo_rol(usuario):
    try:
        return usuario.perfil.rol.codigo
    except PerfilUsuario.DoesNotExist:
        if usuario.is_staff:
            return Rol.Codigos.ADMINISTRADOR
        return Rol.Codigos.CLIENTE


def destino_por_rol(usuario):
    if obtener_codigo_rol(usuario) == Rol.Codigos.ADMINISTRADOR:
        return 'tienda:administracion'
    return 'tienda:inicio'


def rol_requerido(codigo_rol):
    def decorador(vista):
        @login_required(login_url='tienda:login')
        @wraps(vista)
        def vista_protegida(request, *args, **kwargs):
            if obtener_codigo_rol(request.user) != codigo_rol:
                return redirect(destino_por_rol(request.user))
            return vista(request, *args, **kwargs)

        return vista_protegida

    return decorador
