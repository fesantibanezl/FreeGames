from django.urls import path

from . import views


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
    path('recuperar-clave/', views.recuperar_clave, name='recuperar_clave'),
    path('perfil/', views.perfil, name='perfil'),
    path('mis-compras/', views.mis_compras, name='mis_compras'),
    path('compra-exitosa/', views.compra_exitosa, name='compra_exitosa'),
    path('administracion/', views.administracion, name='administracion'),
    path('administracion/juegos/guardar/', views.guardar_juego, name='guardar_juego'),
    path('administracion/juegos/<int:juego_id>/estado/', views.cambiar_estado_juego, name='cambiar_estado_juego'),
    path('administracion/juegos/<int:juego_id>/eliminar/', views.eliminar_juego, name='eliminar_juego'),
    path('administracion/usuarios/<int:usuario_id>/actualizar/', views.actualizar_usuario, name='actualizar_usuario'),
    path('<slug:slug>/', views.categoria, name='categoria'),
]
