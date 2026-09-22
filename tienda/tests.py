from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.db.models.deletion import ProtectedError
from django.test import SimpleTestCase, TestCase
from django.urls import resolve, reverse

from . import views
from .models import PerfilUsuario, Rol


class CatalogoViewsTests(SimpleTestCase):
    def test_inicio_muestra_las_cinco_categorias_y_recursos_estaticos(self):
        respuesta = self.client.get(reverse('tienda:inicio'))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'class="category-row', count=5)
        self.assertContains(respuesta, '/static/tienda/css/style.css')
        self.assertTemplateUsed(respuesta, 'tienda/index.html')

    def test_cada_categoria_muestra_sus_tres_juegos(self):
        for slug in ('accion', 'aventura', 'deportes', 'carreras', 'estrategia'):
            with self.subTest(slug=slug):
                respuesta = self.client.get(reverse('tienda:categoria', kwargs={'slug': slug}))

                self.assertEqual(respuesta.status_code, 200)
                self.assertContains(respuesta, 'class="game-card"', count=3)
                self.assertTemplateUsed(respuesta, 'tienda/categoria.html')

    def test_categoria_desconocida_responde_404(self):
        respuesta = self.client.get(reverse('tienda:categoria', kwargs={'slug': 'desconocida'}))

        self.assertEqual(respuesta.status_code, 404)

    def test_paginas_publicas_renderizan_sus_contenedores(self):
        rutas = {
            'login': ('id="login-form"', 'tienda/login.html'),
            'registro': ('id="registro-form"', 'tienda/registro.html'),
            'recuperar_clave': ('id="recuperar-form"', 'tienda/recuperar_clave.html'),
        }

        for nombre_ruta, (contenedor, template) in rutas.items():
            with self.subTest(nombre_ruta=nombre_ruta):
                respuesta = self.client.get(reverse(f'tienda:{nombre_ruta}'))

                self.assertEqual(respuesta.status_code, 200)
                self.assertContains(respuesta, contenedor)
                self.assertTemplateUsed(respuesta, template)

    def test_categoria_expone_la_grilla_para_el_catalogo_guardado(self):
        respuesta = self.client.get(reverse('tienda:categoria', kwargs={'slug': 'accion'}))

        self.assertContains(respuesta, 'data-products-grid')


class ConfiguracionDjangoTests(SimpleTestCase):
    def test_tienda_esta_registrada_y_sus_rutas_resuelven_vistas(self):
        self.assertIn('tienda.apps.TiendaConfig', settings.INSTALLED_APPS)
        self.assertIs(resolve('/').func, views.inicio)
        self.assertIs(resolve('/accion/').func, views.categoria)
        self.assertIs(resolve('/administracion/').func, views.administracion)

    def test_django_encuentra_los_recursos_estaticos_principales(self):
        recursos = (
            'tienda/css/style.css',
            'tienda/js/productos.js',
            'tienda/js/administracion.js',
            'tienda/img/accion.png',
        )

        for recurso in recursos:
            with self.subTest(recurso=recurso):
                self.assertIsNotNone(finders.find(recurso))


class ModelosUsuarioTests(TestCase):
    def test_migracion_crea_los_dos_roles_solicitados(self):
        codigos = set(Rol.objects.values_list('codigo', flat=True))

        self.assertEqual(
            codigos,
            {Rol.Codigos.CLIENTE, Rol.Codigos.ADMINISTRADOR},
        )

    def test_cuentas_iniciales_tienen_perfil_rol_y_clave_utilizable(self):
        Usuario = get_user_model()
        casos = (
            ('cliente', 'Cliente#2026', Rol.Codigos.CLIENTE, False),
            ('admin', 'Admin#2026', Rol.Codigos.ADMINISTRADOR, True),
        )

        for nombre, clave, rol, es_superusuario in casos:
            with self.subTest(nombre=nombre):
                usuario = Usuario.objects.select_related('perfil__rol').get(
                    username=nombre,
                )

                self.assertTrue(usuario.check_password(clave))
                self.assertEqual(usuario.perfil.rol.codigo, rol)
                self.assertEqual(usuario.is_superuser, es_superusuario)

    def test_un_rol_en_uso_no_puede_eliminarse(self):
        rol_cliente = Rol.objects.get(codigo=Rol.Codigos.CLIENTE)

        with self.assertRaises(ProtectedError):
            rol_cliente.delete()

        self.assertTrue(
            PerfilUsuario.objects.filter(rol=rol_cliente).exists(),
        )


class RegistroYPerfilTests(TestCase):
    def test_registro_crea_usuario_cliente_e_inicia_sesion(self):
        datos = {
            'nombre_completo': 'Alex González',
            'nombre_usuario': 'alexgamer',
            'correo': 'alex@ejemplo.cl',
            'clave': 'Clave#Segura2026',
            'repetir_clave': 'Clave#Segura2026',
            'fecha_nacimiento': '2000-05-15',
            'direccion': 'Avenida Siempre Viva 123',
        }

        respuesta = self.client.post(reverse('tienda:registro'), datos)

        self.assertRedirects(respuesta, reverse('tienda:perfil'))
        Usuario = get_user_model()
        usuario = Usuario.objects.select_related('perfil__rol').get(
            username='alexgamer',
        )
        self.assertTrue(usuario.check_password('Clave#Segura2026'))
        self.assertNotEqual(usuario.password, 'Clave#Segura2026')
        self.assertEqual(usuario.perfil.rol.codigo, Rol.Codigos.CLIENTE)
        self.assertEqual(
            int(self.client.session['_auth_user_id']),
            usuario.pk,
        )

    def test_registro_rechaza_usuario_y_correo_duplicados(self):
        respuesta = self.client.post(
            reverse('tienda:registro'),
            {
                'nombre_completo': 'Otro Cliente',
                'nombre_usuario': 'CLIENTE',
                'correo': 'CLIENTE@FREEGAMES.CL',
                'clave': 'Clave#Segura2026',
                'repetir_clave': 'Clave#Segura2026',
                'fecha_nacimiento': '2000-05-15',
                'direccion': '',
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta,
            'Ese nombre de usuario ya está registrado.',
        )
        self.assertContains(
            respuesta,
            'Ese correo electrónico ya está registrado.',
        )
        self.assertEqual(
            get_user_model().objects.filter(username__iexact='cliente').count(),
            1,
        )

    def test_perfil_requiere_usuario_autenticado(self):
        respuesta = self.client.get(reverse('tienda:perfil'))

        self.assertRedirects(
            respuesta,
            f"{reverse('tienda:login')}?next={reverse('tienda:perfil')}",
            fetch_redirect_response=False,
        )

    def test_perfil_muestra_y_modifica_los_datos_persistentes(self):
        Usuario = get_user_model()
        usuario = Usuario.objects.get(username='cliente')
        clave_anterior = usuario.password
        self.client.force_login(usuario)

        respuesta = self.client.get(reverse('tienda:perfil'))
        self.assertContains(respuesta, 'Cliente FreeGames')
        self.assertContains(respuesta, 'value="Cliente"')

        respuesta = self.client.post(
            reverse('tienda:perfil'),
            {
                'nombre_completo': 'Cliente Actualizado',
                'nombre_usuario': 'clienteactual',
                'correo': 'actualizado@freegames.cl',
                'fecha_nacimiento': '1999-06-10',
                'direccion': 'Calle Nueva 456, Santiago',
            },
        )

        self.assertRedirects(respuesta, reverse('tienda:perfil'))
        usuario.refresh_from_db()
        usuario.perfil.refresh_from_db()
        self.assertEqual(usuario.get_full_name(), 'Cliente Actualizado')
        self.assertEqual(usuario.username, 'clienteactual')
        self.assertEqual(usuario.email, 'actualizado@freegames.cl')
        self.assertEqual(usuario.perfil.direccion, 'Calle Nueva 456, Santiago')
        self.assertEqual(usuario.perfil.rol.codigo, Rol.Codigos.CLIENTE)
        self.assertEqual(usuario.password, clave_anterior)


class AutenticacionYRolesTests(TestCase):
    def setUp(self):
        Usuario = get_user_model()
        self.cliente = Usuario.objects.get(username='cliente')
        self.administrador = Usuario.objects.get(username='admin')

    def test_login_acepta_usuario_para_cliente_y_correo_para_administrador(self):
        respuesta = self.client.post(
            reverse('tienda:login'),
            {'acceso': 'CLIENTE', 'clave': 'Cliente#2026'},
        )
        self.assertRedirects(respuesta, reverse('tienda:inicio'))
        self.assertEqual(
            int(self.client.session['_auth_user_id']),
            self.cliente.pk,
        )

        self.client.logout()
        respuesta = self.client.post(
            reverse('tienda:login'),
            {'acceso': 'ADMIN@FREEGAMES.CL', 'clave': 'Admin#2026'},
        )
        self.assertRedirects(
            respuesta,
            reverse('tienda:administracion'),
        )
        self.assertEqual(
            int(self.client.session['_auth_user_id']),
            self.administrador.pk,
        )

    def test_login_informa_credenciales_invalidas_y_cuenta_inactiva(self):
        respuesta = self.client.post(
            reverse('tienda:login'),
            {'acceso': 'cliente', 'clave': 'Incorrecta#2026'},
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta,
            'No fue posible iniciar sesión. Revisa tus credenciales.',
        )

        self.cliente.is_active = False
        self.cliente.save(update_fields=('is_active',))
        respuesta = self.client.post(
            reverse('tienda:login'),
            {'acceso': 'cliente', 'clave': 'Cliente#2026'},
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta,
            'La cuenta está desactivada. Contacta al administrador.',
        )

    def test_login_respeta_destino_interno_del_cliente(self):
        destino = reverse('tienda:carrito')
        respuesta = self.client.post(
            reverse('tienda:login'),
            {
                'acceso': 'cliente',
                'clave': 'Cliente#2026',
                'siguiente': destino,
            },
        )

        self.assertRedirects(respuesta, destino)

    def test_logout_solo_acepta_post_y_elimina_la_sesion(self):
        self.client.force_login(self.cliente)

        respuesta = self.client.get(reverse('tienda:logout'))
        self.assertEqual(respuesta.status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)

        respuesta = self.client.post(reverse('tienda:logout'))
        self.assertRedirects(respuesta, reverse('tienda:inicio'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_paginas_internas_redirigen_al_login_sin_sesion(self):
        for nombre_ruta in (
            'perfil',
            'carrito',
            'mis_compras',
            'compra_exitosa',
            'administracion',
        ):
            with self.subTest(nombre_ruta=nombre_ruta):
                ruta = reverse(f'tienda:{nombre_ruta}')
                respuesta = self.client.get(ruta)
                self.assertRedirects(
                    respuesta,
                    f"{reverse('tienda:login')}?next={ruta}",
                    fetch_redirect_response=False,
                )

    def test_cliente_accede_a_sus_paginas_y_no_al_panel_administrativo(self):
        self.client.force_login(self.cliente)
        paginas_cliente = {
            'perfil': 'id="perfil-form"',
            'carrito': 'id="cart-page"',
            'mis_compras': 'id="history-content"',
            'compra_exitosa': 'id="purchase-result"',
        }

        for nombre_ruta, contenedor in paginas_cliente.items():
            with self.subTest(nombre_ruta=nombre_ruta):
                respuesta = self.client.get(reverse(f'tienda:{nombre_ruta}'))
                self.assertEqual(respuesta.status_code, 200)
                self.assertContains(respuesta, contenedor)

        respuesta = self.client.get(reverse('tienda:administracion'))
        self.assertRedirects(respuesta, reverse('tienda:inicio'))

    def test_administrador_accede_al_panel_y_es_redirigido_desde_area_cliente(self):
        self.client.force_login(self.administrador)
        respuesta = self.client.get(reverse('tienda:administracion'))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, '/static/tienda/js/administracion.js')
        self.assertContains(respuesta, 'data-action="new-product"')
        self.assertContains(respuesta, 'id="admin-product-description"')

        for nombre_ruta in (
            'inicio',
            'perfil',
            'carrito',
            'mis_compras',
            'compra_exitosa',
        ):
            with self.subTest(nombre_ruta=nombre_ruta):
                respuesta = self.client.get(reverse(f'tienda:{nombre_ruta}'))
                self.assertRedirects(
                    respuesta,
                    reverse('tienda:administracion'),
                )

        respuesta = self.client.get(
            reverse('tienda:categoria', kwargs={'slug': 'accion'}),
        )
        self.assertRedirects(respuesta, reverse('tienda:administracion'))

    def test_navegacion_se_adapta_a_la_sesion_y_al_rol(self):
        respuesta = self.client.get(reverse('tienda:inicio'))
        self.assertContains(respuesta, 'Iniciar sesión')
        self.assertContains(respuesta, 'Registrarse')
        self.assertNotContains(respuesta, 'Cerrar sesión')

        self.client.force_login(self.cliente)
        respuesta = self.client.get(reverse('tienda:inicio'))
        self.assertContains(respuesta, 'Mi perfil: cliente')
        self.assertContains(respuesta, 'Mis compras')
        self.assertContains(respuesta, 'Cerrar sesión')
        self.assertNotContains(respuesta, '>Administración</a>')
        self.assertContains(respuesta, 'rol: "cliente"')

        self.client.force_login(self.administrador)
        respuesta = self.client.get(reverse('tienda:administracion'))
        self.assertContains(respuesta, '>Administración</a>')
        self.assertContains(respuesta, 'Cerrar sesión')
        self.assertNotContains(respuesta, '>Acción</a>')
        self.assertNotContains(respuesta, 'Mi perfil:')
        self.assertContains(respuesta, 'rol: "administrador"')
