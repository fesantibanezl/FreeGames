from django.contrib import messages
from django.contrib.auth import login as iniciar_sesion
from django.contrib.auth import logout as cerrar_sesion_django
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .catalogo import CATEGORIAS
from .decorators import destino_por_rol, obtener_codigo_rol, rol_requerido
from .forms import InicioSesionForm, PerfilUsuarioForm, RegistroUsuarioForm
from .models import PerfilUsuario, Rol


def inicio(request):
    """Muestra la página inicial de FreeGames."""
    if (
        request.user.is_authenticated
        and obtener_codigo_rol(request.user) == Rol.Codigos.ADMINISTRADOR
    ):
        return redirect('tienda:administracion')

    contexto = {
        'categorias': CATEGORIAS.values(),
        'seccion_activa': 'inicio',
    }
    return render(request, 'tienda/index.html', contexto)


def categoria(request, slug):
    """Muestra los juegos de una categoría del catálogo."""
    if (
        request.user.is_authenticated
        and obtener_codigo_rol(request.user) == Rol.Codigos.ADMINISTRADOR
    ):
        return redirect('tienda:administracion')

    categoria_seleccionada = CATEGORIAS.get(slug)

    if categoria_seleccionada is None:
        raise Http404('La categoría solicitada no existe.')

    contexto = {
        'categoria': categoria_seleccionada,
        'encabezado_compacto': True,
        'seccion_activa': slug,
    }
    return render(request, 'tienda/categoria.html', contexto)


def registro(request):
    if request.user.is_authenticated:
        return redirect(destino_por_rol(request.user))

    datos_formulario = request.POST if request.method == 'POST' else None
    formulario = RegistroUsuarioForm(datos_formulario)
    if request.method == 'POST' and formulario.is_valid():
        usuario = formulario.save()
        iniciar_sesion(request, usuario)
        messages.success(
            request,
            'Cuenta creada correctamente. Ya puedes administrar tu perfil.',
        )
        return redirect('tienda:perfil')

    return render(request, 'tienda/registro.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'registro',
        'formulario': formulario,
    })


def login(request):
    if request.user.is_authenticated:
        return redirect(destino_por_rol(request.user))

    datos_formulario = request.POST if request.method == 'POST' else None
    formulario = InicioSesionForm(datos_formulario, request=request)
    siguiente = request.POST.get('siguiente') or request.GET.get('next', '')

    if request.method == 'POST' and formulario.is_valid():
        usuario = formulario.usuario
        iniciar_sesion(request, usuario)

        if (
            obtener_codigo_rol(usuario) == Rol.Codigos.CLIENTE
            and siguiente
            and url_has_allowed_host_and_scheme(
                siguiente,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            )
        ):
            return redirect(siguiente)
        return redirect(destino_por_rol(usuario))

    return render(request, 'tienda/login.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'login',
        'formulario': formulario,
        'siguiente': siguiente,
    })


@require_POST
def logout(request):
    cerrar_sesion_django(request)
    return redirect('tienda:inicio')


def recuperar_clave(request):
    return render(request, 'tienda/recuperar_clave.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'recuperar_clave',
    })


@rol_requerido(Rol.Codigos.CLIENTE)
def perfil(request):
    rol_predeterminado = Rol.objects.get(codigo=Rol.Codigos.CLIENTE)
    perfil_usuario, _ = PerfilUsuario.objects.get_or_create(
        usuario=request.user,
        defaults={'rol': rol_predeterminado},
    )
    datos_formulario = request.POST if request.method == 'POST' else None
    formulario = PerfilUsuarioForm(
        datos_formulario,
        usuario=request.user,
        perfil=perfil_usuario,
    )
    if request.method == 'POST' and formulario.is_valid():
        formulario.save()
        messages.success(
            request,
            'Los datos del perfil se actualizaron correctamente.',
        )
        return redirect('tienda:perfil')

    return render(request, 'tienda/perfil.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'perfil',
        'formulario': formulario,
        'rol_nombre': perfil_usuario.rol.nombre,
    })


@rol_requerido(Rol.Codigos.CLIENTE)
def carrito(request):
    return render(request, 'tienda/carrito.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'carrito',
    })


@rol_requerido(Rol.Codigos.CLIENTE)
def compra_exitosa(request):
    return render(request, 'tienda/compra_exitosa.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'compra_exitosa',
    })


@rol_requerido(Rol.Codigos.CLIENTE)
def mis_compras(request):
    return render(request, 'tienda/mis_compras.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'mis_compras',
    })


@rol_requerido(Rol.Codigos.ADMINISTRADOR)
def administracion(request):
    return render(request, 'tienda/administracion.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'administracion',
    })
