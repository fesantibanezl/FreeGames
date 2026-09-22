from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import DefinirClaveForm, RecuperacionClaveForm


app_name = 'tienda'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('carrito/', views.carrito, name='carrito'),
    path('carrito/agregar/<int:juego_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/actualizar/<int:juego_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/quitar/<int:juego_id>/', views.quitar_carrito, name='quitar_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('carrito/finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('registro/', views.registro, name='registro'),
    path(
        'recuperar-clave/',
        auth_views.PasswordResetView.as_view(
            template_name='tienda/recuperar_clave.html',
            form_class=RecuperacionClaveForm,
            email_template_name='tienda/correo_recuperacion.txt',
            subject_template_name='tienda/asunto_recuperacion.txt',
            success_url=reverse_lazy('tienda:recuperar_clave_enviada'),
            extra_context={
                'encabezado_compacto': True,
                'seccion_activa': 'recuperar_clave',
            },
        ),
        name='recuperar_clave',
    ),
    path(
        'recuperar-clave/enviada/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='tienda/recuperar_clave_enviada.html',
            extra_context={'encabezado_compacto': True},
        ),
        name='recuperar_clave_enviada',
    ),
    path(
        'recuperar-clave/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='tienda/recuperar_clave_confirmar.html',
            form_class=DefinirClaveForm,
            success_url=reverse_lazy('tienda:recuperar_clave_completa'),
            extra_context={'encabezado_compacto': True},
        ),
        name='recuperar_clave_confirmar',
    ),
    path(
        'recuperar-clave/completa/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='tienda/recuperar_clave_completa.html',
            extra_context={'encabezado_compacto': True},
        ),
        name='recuperar_clave_completa',
    ),
    path('perfil/', views.perfil, name='perfil'),
    path('mis-compras/', views.mis_compras, name='mis_compras'),
    path('compra-exitosa/', views.compra_exitosa, name='compra_exitosa'),
    path('administracion/', views.administracion, name='administracion'),
    path('administracion/juegos/guardar/', views.guardar_juego, name='guardar_juego'),
    path('administracion/juegos/<int:juego_id>/estado/', views.cambiar_estado_juego, name='cambiar_estado_juego'),
    path('administracion/juegos/<int:juego_id>/eliminar/', views.eliminar_juego, name='eliminar_juego'),
    path('administracion/usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('administracion/usuarios/<int:usuario_id>/actualizar/', views.actualizar_usuario, name='actualizar_usuario'),
    path('administracion/usuarios/<int:usuario_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    path('<slug:slug>/', views.categoria, name='categoria'),
]
