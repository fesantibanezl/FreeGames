from django.contrib import messages
from django.contrib.auth import login as iniciar_sesion
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render

from .catalogo import CATEGORIAS
from .forms import PerfilUsuarioForm, RegistroUsuarioForm
from .models import PerfilUsuario, Rol


def inicio(request):
    """Muestra la página inicial de FreeGames."""
    contexto = {
        'categorias': CATEGORIAS.values(),
        'seccion_activa': 'inicio',
    }
    return render(request, 'tienda/index.html', contexto)


def categoria(request, slug):
    """Muestra los juegos de una categoría del catálogo."""
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
    return render(request, 'tienda/login.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'login',
    })


def recuperar_clave(request):
    return render(request, 'tienda/recuperar_clave.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'recuperar_clave',
    })


@login_required(login_url='tienda:login')
def perfil(request):
    codigo_rol = (
        Rol.Codigos.ADMINISTRADOR
        if request.user.is_staff
        else Rol.Codigos.CLIENTE
    )
    rol_predeterminado = Rol.objects.get(codigo=codigo_rol)
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


def carrito(request):
    return render(request, 'tienda/carrito.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'carrito',
    })


def compra_exitosa(request):
    return render(request, 'tienda/compra_exitosa.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'compra_exitosa',
    })


def mis_compras(request):
    return render(request, 'tienda/mis_compras.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'mis_compras',
    })


def administracion(request):
    return render(request, 'tienda/administracion.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'administracion',
    })
