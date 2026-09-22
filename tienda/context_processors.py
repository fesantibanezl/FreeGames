from .decorators import obtener_codigo_rol


def sesion_freegames(request):
    """Expone el rol autenticado a todas las plantillas de la tienda."""
    if not request.user.is_authenticated:
        return {'rol_actual': ''}

    return {'rol_actual': obtener_codigo_rol(request.user)}
