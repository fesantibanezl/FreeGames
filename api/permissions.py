from rest_framework.permissions import BasePermission, SAFE_METHODS

from tienda.models import PerfilUsuario, Rol


class EsAdministradorOConsulta(BasePermission):
    """Permite consultar con token y reserva los cambios al administrador."""

    message = 'Solo los administradores pueden modificar estos recursos.'

    def has_permission(self, request, view):
        usuario = request.user
        if not usuario or not usuario.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if usuario.is_staff or usuario.is_superuser:
            return True
        return PerfilUsuario.objects.filter(
            usuario=usuario,
            rol__codigo=Rol.Codigos.ADMINISTRADOR,
        ).exists()
