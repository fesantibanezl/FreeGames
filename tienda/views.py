from django.shortcuts import render


def inicio(request):
    """Muestra la página inicial de FreeGames."""
    contexto = {
        'titulo': 'FreeGames',
        'mensaje': 'El proyecto Django está configurado correctamente.',
    }
    return render(request, 'tienda/index.html', contexto)
