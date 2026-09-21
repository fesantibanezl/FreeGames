from django.urls import path

from . import views


app_name = 'tienda'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('carrito/', views.pagina_pendiente, {'nombre': 'Carrito', 'seccion': 'carrito'}, name='carrito'),
    path('login/', views.pagina_pendiente, {'nombre': 'Iniciar sesión', 'seccion': 'login'}, name='login'),
    path('registro/', views.pagina_pendiente, {'nombre': 'Registro', 'seccion': 'registro'}, name='registro'),
    path('recuperar-clave/', views.pagina_pendiente, {'nombre': 'Recuperar contraseña', 'seccion': 'recuperar_clave'}, name='recuperar_clave'),
    path('perfil/', views.pagina_pendiente, {'nombre': 'Mi perfil', 'seccion': 'perfil'}, name='perfil'),
    path('mis-compras/', views.pagina_pendiente, {'nombre': 'Mis compras', 'seccion': 'mis_compras'}, name='mis_compras'),
    path('compra-exitosa/', views.pagina_pendiente, {'nombre': 'Compra exitosa', 'seccion': 'compra_exitosa'}, name='compra_exitosa'),
    path('administracion/', views.pagina_pendiente, {'nombre': 'Administración', 'seccion': 'administracion'}, name='administracion'),
    path('<slug:slug>/', views.categoria, name='categoria'),
]
