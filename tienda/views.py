from django.http import Http404
from django.shortcuts import render

from .catalogo import CATEGORIAS


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
    return render(request, 'tienda/registro.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'registro',
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


def perfil(request):
    return render(request, 'tienda/perfil.html', {
        'encabezado_compacto': True,
        'seccion_activa': 'perfil',
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
