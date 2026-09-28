from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views


app_name = 'api'

urlpatterns = [
    path('token/', obtain_auth_token, name='token'),
    path('categorias/', views.categorias, name='categorias'),
    path(
        'categorias/<int:categoria_id>/',
        views.categoria_detalle,
        name='categoria_detalle',
    ),
    path('juegos/', views.juegos, name='juegos'),
    path(
        'juegos/<int:juego_id>/',
        views.juego_detalle,
        name='juego_detalle',
    ),
]
