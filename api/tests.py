from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from tienda.models import Categoria, Juego


class ConfiguracionApiTests(SimpleTestCase):
    def test_aplicaciones_requeridas_estan_registradas(self):
        self.assertIn('rest_framework', settings.INSTALLED_APPS)
        self.assertIn('rest_framework.authtoken', settings.INSTALLED_APPS)
        self.assertIn('corsheaders', settings.INSTALLED_APPS)
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
        self.assertFalse(settings.CORS_ALLOW_CREDENTIALS)
        self.assertEqual(settings.CORS_URLS_REGEX, r'^/api/')


class CorsApiTests(SimpleTestCase):
    @override_settings(CORS_ALLOWED_ORIGINS=['http://localhost:3000'])
    def test_origen_autorizado_recibe_preflight_sin_eludir_token(self):
        casos = (
            ('api:token', 'POST', 'content-type'),
            ('api:categorias', 'GET', 'authorization'),
            ('api:juegos', 'GET', 'authorization'),
        )
        for nombre, metodo, encabezado in casos:
            with self.subTest(nombre=nombre):
                preflight = self.client.options(
                    reverse(nombre),
                    HTTP_ORIGIN='http://localhost:3000',
                    HTTP_ACCESS_CONTROL_REQUEST_METHOD=metodo,
                    HTTP_ACCESS_CONTROL_REQUEST_HEADERS=encabezado,
                )
                self.assertEqual(preflight.status_code, status.HTTP_200_OK)
                self.assertEqual(
                    preflight['Access-Control-Allow-Origin'],
                    'http://localhost:3000',
                )
                self.assertIn(
                    encabezado,
                    preflight['Access-Control-Allow-Headers'],
                )

        respuesta = self.client.get(
            reverse('api:juegos'),
            HTTP_ORIGIN='http://localhost:3000',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            respuesta['Access-Control-Allow-Origin'],
            'http://localhost:3000',
        )

    @override_settings(CORS_ALLOWED_ORIGINS=['http://localhost:3000'])
    def test_origen_no_autorizado_y_paginas_no_reciben_cors(self):
        respuesta = self.client.get(
            reverse('api:juegos'),
            HTTP_ORIGIN='https://sitio-desconocido.test',
        )
        self.assertNotIn('Access-Control-Allow-Origin', respuesta)

        respuesta_pagina = self.client.get(
            reverse('tienda:login'),
            HTTP_ORIGIN='http://localhost:3000',
        )
        self.assertNotIn('Access-Control-Allow-Origin', respuesta_pagina)


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

    def test_ambas_apis_rechazan_consultas_sin_token(self):
        categoria = Categoria.objects.first()
        juego = Juego.objects.first()
        rutas = (
            reverse('api:categorias'),
            reverse(
                'api:categoria_detalle',
                kwargs={'categoria_id': categoria.pk},
            ),
            reverse('api:juegos'),
            reverse('api:juego_detalle', kwargs={'juego_id': juego.pk}),
        )

        for ruta in rutas:
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta)
                self.assertEqual(
                    respuesta.status_code,
                    status.HTTP_401_UNAUTHORIZED,
                )

    def test_sesion_web_sin_token_no_sustituye_autenticacion_api(self):
        self.client.force_login(self.cliente)

        for nombre in ('api:categorias', 'api:juegos'):
            with self.subTest(nombre=nombre):
                respuesta = self.client.get(reverse(nombre))
                self.assertEqual(
                    respuesta.status_code,
                    status.HTTP_401_UNAUTHORIZED,
                )

    def test_navegador_con_csrf_habilitado_puede_obtener_token(self):
        navegador = APIClient(enforce_csrf_checks=True)

        respuesta = navegador.post(
            reverse('api:token'),
            {'username': 'cliente', 'password': 'Cliente#2026'},
            format='json',
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn('token', respuesta.data)

    def test_ambas_apis_rechazan_token_invalido(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token token-inexistente')

        for nombre in ('api:categorias', 'api:juegos'):
            with self.subTest(nombre=nombre):
                respuesta = self.client.get(reverse(nombre))
                self.assertEqual(
                    respuesta.status_code,
                    status.HTTP_401_UNAUTHORIZED,
                )

    def test_token_obtenido_por_login_consulta_ambas_apis(self):
        respuesta_token = self.client.post(
            reverse('api:token'),
            {'username': 'cliente', 'password': 'Cliente#2026'},
            format='json',
        )
        self.assertEqual(respuesta_token.status_code, status.HTTP_200_OK)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {respuesta_token.data['token']}",
        )

        for nombre in ('api:categorias', 'api:juegos'):
            with self.subTest(nombre=nombre):
                respuesta = self.client.get(reverse(nombre))
                self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
                self.assertGreater(len(respuesta.data), 0)

    def test_cliente_con_token_no_puede_escribir_en_ninguna_api(self):
        self.autenticar_con_token(self.cliente)
        categoria = Categoria.objects.first()
        juego = Juego.objects.first()
        colecciones = (reverse('api:categorias'), reverse('api:juegos'))
        detalles = (
            reverse(
                'api:categoria_detalle',
                kwargs={'categoria_id': categoria.pk},
            ),
            reverse('api:juego_detalle', kwargs={'juego_id': juego.pk}),
        )

        for ruta in colecciones:
            with self.subTest(metodo='POST', ruta=ruta):
                respuesta = self.client.post(ruta, {}, format='json')
                self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
        for ruta in detalles:
            for metodo in ('patch', 'delete'):
                with self.subTest(metodo=metodo, ruta=ruta):
                    respuesta = getattr(self.client, metodo)(
                        ruta, {}, format='json',
                    )
                    self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_administrador_con_token_puede_crear_juego(self):
        self.autenticar_con_token(self.administrador)
        categoria = Categoria.objects.first()
        datos = {
            'categoria': categoria.pk,
            'slug': 'nuevo-juego-api',
            'nombre': 'Nuevo juego API',
            'descripcion': 'Juego creado para verificar el permiso con token.',
            'precio': 0,
            'stock': 10,
            'activo': True,
            'imagen': 'tienda/img/accion.png',
            'imagen_alt': 'Portada del nuevo juego API',
        }

        respuesta = self.client.post(reverse('api:juegos'), datos, format='json')

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Juego.objects.filter(slug='nuevo-juego-api').exists())

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
