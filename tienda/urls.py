from django.urls import path

from . import views


app_name = 'tienda'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('carrito/', views.carrito, name='carrito'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('registro/', views.registro, name='registro'),
    path('recuperar-clave/', views.recuperar_clave, name='recuperar_clave'),
    path('perfil/', views.perfil, name='perfil'),
    path('mis-compras/', views.mis_compras, name='mis_compras'),
    path('compra-exitosa/', views.compra_exitosa, name='compra_exitosa'),
    path('administracion/', views.administracion, name='administracion'),
    path('<slug:slug>/', views.categoria, name='categoria'),
]
