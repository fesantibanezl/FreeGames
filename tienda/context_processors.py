from .decorators import obtener_codigo_rol


def sesion_freegames(request):
    """Expone el rol autenticado a todas las plantillas de la tienda."""
    if not request.user.is_authenticated:
        return {'rol_actual': '', 'cantidad_carrito': 0}

    carrito = request.session.get('freegames_carrito', {})
    cantidad_carrito = 0
    if isinstance(carrito, dict):
        for cantidad in carrito.values():
            try:
                cantidad_carrito += max(0, int(cantidad))
            except (TypeError, ValueError):
                continue

    return {
        'rol_actual': obtener_codigo_rol(request.user),
        'cantidad_carrito': cantidad_carrito,
    }
