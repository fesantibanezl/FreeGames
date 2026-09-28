from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
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

        respuesta = self.client.get(detalle)
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)

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


class SeguridadYFiltrosApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        Usuario = get_user_model()
        self.cliente = Usuario.objects.get(username='cliente')
        self.administrador = Usuario.objects.get(username='admin')

    def autenticar_con_token(self, usuario):
        token, _ = Token.objects.get_or_create(user=usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def datos_categoria(self):
        return {
            'slug': 'simulacion',
            'nombre': 'Simulación',
            'icono': 'SIM',
            'clase_css': 'category-simulation',
            'resumen': 'Experiencias de simulación',
            'descripcion_meta': 'Juegos de simulación de FreeGames.',
            'imagen': 'tienda/img/estrategia.png',
            'imagen_alt': 'Escena de un videojuego de simulación',
            'orden': 7,
        }

    def test_token_se_obtiene_con_credenciales_validas(self):
        respuesta = self.client.post(
            reverse('api:token'),
            {
                'username': 'cliente',
                'password': 'Cliente#2026',
            },
            format='json',
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn('token', respuesta.data)
        self.assertTrue(
            Token.objects.filter(
                user=self.cliente,
                key=respuesta.data['token'],
            ).exists(),
        )

    def test_token_rechaza_credenciales_invalidas(self):
        respuesta = self.client.post(
            reverse('api:token'),
            {'username': 'cliente', 'password': 'incorrecta'},
            format='json',
        )

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', respuesta.data)

    def test_recurso_sin_token_responde_401(self):
        respuesta = self.client.get(reverse('api:juegos'))

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_token_invalido_responde_401(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token token-inexistente')

        respuesta = self.client.get(reverse('api:juegos'))

        self.assertEqual(
            respuesta.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_cliente_con_token_puede_consultar(self):
        self.autenticar_con_token(self.cliente)

        respuesta = self.client.get(reverse('api:juegos'))

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_cliente_con_token_no_puede_crear(self):
        self.autenticar_con_token(self.cliente)

        respuesta = self.client.post(
            reverse('api:categorias'),
            self.datos_categoria(),
            format='json',
        )

        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Categoria.objects.filter(slug='simulacion').exists())

    def test_cliente_no_puede_modificar_ni_eliminar(self):
        self.autenticar_con_token(self.cliente)
        juego = Juego.objects.first()
        stock_original = juego.stock
        ruta = reverse('api:juego_detalle', kwargs={'juego_id': juego.pk})

        respuesta = self.client.patch(ruta, {'stock': 999}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

        respuesta = self.client.delete(ruta)
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

        juego.refresh_from_db()
        self.assertEqual(juego.stock, stock_original)

    def test_administrador_con_token_puede_crear(self):
        self.autenticar_con_token(self.administrador)

        respuesta = self.client.post(
            reverse('api:categorias'),
            self.datos_categoria(),
            format='json',
        )

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Categoria.objects.filter(slug='simulacion').exists())

    def test_filtra_juegos_por_nombre(self):
        self.autenticar_con_token(self.cliente)

        respuesta = self.client.get(
            reverse('api:juegos'),
            {'nombre': 'valorant'},
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertGreater(len(respuesta.data), 0)
        self.assertTrue(
            all('valorant' in juego['nombre'].lower() for juego in respuesta.data),
        )

    def test_filtra_juegos_por_categoria(self):
        self.autenticar_con_token(self.cliente)

        respuesta = self.client.get(
            reverse('api:juegos'),
            {'categoria': 'accion'},
        )

        esperados = Juego.objects.filter(categoria__slug='accion').count()
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.data), esperados)
        self.assertTrue(
            all(juego['categoria_nombre'] == 'Acción' for juego in respuesta.data),
        )

    def test_filtra_juegos_por_estado_y_gratuidad(self):
        juego_oculto = Juego.objects.filter(precio=0).first()
        juego_oculto.activo = False
        juego_oculto.save(update_fields=('activo',))
        self.autenticar_con_token(self.cliente)

        respuesta = self.client.get(
            reverse('api:juegos'),
            {'activo': 'false', 'gratis': 'true'},
        )

        esperados = Juego.objects.filter(activo=False, precio=0).count()
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.data), esperados)
        self.assertTrue(all(not juego['activo'] for juego in respuesta.data))
        self.assertTrue(all(juego['gratis'] for juego in respuesta.data))

    def test_filtro_booleano_invalido_responde_400(self):
        self.autenticar_con_token(self.cliente)

        respuesta = self.client.get(
            reverse('api:juegos'),
            {'activo': 'talvez'},
        )

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('activo', respuesta.data)

    def test_filtro_sin_coincidencias_devuelve_lista_vacia(self):
        self.autenticar_con_token(self.cliente)

        respuesta = self.client.get(
            reverse('api:juegos'),
            {'nombre': 'titulo-que-no-existe'},
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data, [])
