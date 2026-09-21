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


def pagina_pendiente(request, nombre, seccion):
    """Mantiene navegables las rutas que serán migradas en la Parte 3."""
    contexto = {
        'titulo': nombre,
        'encabezado_compacto': True,
        'seccion_activa': seccion,
    }
    return render(request, 'tienda/migracion_pendiente.html', contexto)
