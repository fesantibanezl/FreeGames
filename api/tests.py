from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tienda.models import Categoria, Juego


class ConfiguracionApiTests(SimpleTestCase):
    def test_aplicaciones_requeridas_estan_registradas(self):
        self.assertIn('rest_framework', settings.INSTALLED_APPS)
        self.assertIn('rest_framework.authtoken', settings.INSTALLED_APPS)
        self.assertIn('api.apps.ApiConfig', settings.INSTALLED_APPS)

    def test_autenticacion_y_permisos_son_restrictivos_por_defecto(self):
        self.assertEqual(
            settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'],
            ['rest_framework.authentication.TokenAuthentication'],
        )
        self.assertEqual(
            settings.REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'],
            ['rest_framework.permissions.IsAuthenticated'],
        )


class CrudApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.usuario = get_user_model().objects.get(username='admin')
        self.client.force_authenticate(user=self.usuario)

    def datos_categoria(self, **cambios):
        datos = {
            'slug': 'rol',
            'nombre': 'Rol',
            'icono': 'RPG',
            'clase_css': 'category-rpg',
            'resumen': 'Historias y evolución de personajes',
            'descripcion_meta': 'Juegos de rol disponibles en FreeGames.',
            'imagen': 'tienda/img/aventura.png',
            'imagen_alt': 'Personajes de un videojuego de rol',
            'orden': 6,
        }
        datos.update(cambios)
        return datos

    def crear_categoria(self):
        return Categoria.objects.create(**self.datos_categoria())

    def datos_juego(self, categoria, **cambios):
        datos = {
            'categoria': categoria.pk,
            'slug': 'aventura-api',
            'nombre': 'Aventura API',
            'descripcion': 'Juego creado para comprobar la API REST.',
            'precio': 0,
            'stock': 20,
            'activo': True,
            'imagen': 'tienda/img/aventura.png',
            'imagen_alt': 'Escena del juego Aventura API',
        }
        datos.update(cambios)
        return datos

    def test_lista_categorias_serializadas(self):
        respuesta = self.client.get(reverse('api:categorias'))

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.data), 5)
        self.assertIn('slug', respuesta.data[0])

    def test_crud_completo_de_categoria(self):
        respuesta = self.client.post(
            reverse('api:categorias'),
            self.datos_categoria(),
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        categoria_id = respuesta.data['id']

        detalle = reverse(
            'api:categoria_detalle',
            kwargs={'categoria_id': categoria_id},
        )
        respuesta = self.client.get(detalle)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data['nombre'], 'Rol')

        datos_actualizados = self.datos_categoria(nombre='Rol y fantasía')
        respuesta = self.client.put(detalle, datos_actualizados, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data['nombre'], 'Rol y fantasía')

        respuesta = self.client.delete(detalle)
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Categoria.objects.filter(pk=categoria_id).exists())

    def test_categoria_invalida_responde_400(self):
        respuesta = self.client.post(
            reverse('api:categorias'),
            self.datos_categoria(nombre=''),
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('nombre', respuesta.data)

    def test_categoria_inexistente_responde_404(self):
        respuesta = self.client.get(
            reverse(
                'api:categoria_detalle',
                kwargs={'categoria_id': 999999},
            ),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)

    def test_categoria_con_juegos_no_se_elimina(self):
        categoria = Categoria.objects.get(slug='accion')
        respuesta = self.client.delete(
            reverse(
                'api:categoria_detalle',
                kwargs={'categoria_id': categoria.pk},
            ),
        )

        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(Categoria.objects.filter(pk=categoria.pk).exists())

    def test_lista_juegos_incluye_categoria_y_campo_gratis(self):
        respuesta = self.client.get(reverse('api:juegos'))

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.data), 15)
        self.assertIn('categoria_nombre', respuesta.data[0])
        self.assertIn('gratis', respuesta.data[0])

    def test_crud_completo_de_juego(self):
        categoria = self.crear_categoria()
        respuesta = self.client.post(
            reverse('api:juegos'),
            self.datos_juego(categoria),
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        juego_id = respuesta.data['id']
        self.assertTrue(respuesta.data['gratis'])

        detalle = reverse(
            'api:juego_detalle',
            kwargs={'juego_id': juego_id},
        )
        respuesta = self.client.get(detalle)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data['categoria_nombre'], 'Rol')

        respuesta = self.client.patch(
            detalle,
            {'precio': 15990, 'stock': 8},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data['precio'], 15990)
        self.assertFalse(respuesta.data['gratis'])

        respuesta = self.client.delete(detalle)
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Juego.objects.filter(pk=juego_id).exists())

    def test_juego_invalido_responde_400(self):
        categoria = self.crear_categoria()
        respuesta = self.client.post(
            reverse('api:juegos'),
            self.datos_juego(categoria, precio=-1),
            format='json',
        )

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('precio', respuesta.data)

    def test_juego_inexistente_responde_404(self):
        respuesta = self.client.get(
            reverse('api:juego_detalle', kwargs={'juego_id': 999999}),
        )
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)
