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

    def test_paginas_funcionales_renderizan_sus_contenedores(self):
        rutas = {
            'carrito': ('id="cart-page"', 'tienda/carrito.html'),
            'login': ('id="login-form"', 'tienda/login.html'),
            'registro': ('id="registro-form"', 'tienda/registro.html'),
            'recuperar_clave': ('id="recuperar-form"', 'tienda/recuperar_clave.html'),
            'perfil': ('id="perfil-form"', 'tienda/perfil.html'),
            'mis_compras': ('id="history-content"', 'tienda/mis_compras.html'),
            'compra_exitosa': ('id="purchase-result"', 'tienda/compra_exitosa.html'),
            'administracion': ('id="administration-content"', 'tienda/administracion.html'),
        }

        for nombre_ruta, (contenedor, template) in rutas.items():
            with self.subTest(nombre_ruta=nombre_ruta):
                respuesta = self.client.get(reverse(f'tienda:{nombre_ruta}'))

                self.assertEqual(respuesta.status_code, 200)
                self.assertContains(respuesta, contenedor)
                self.assertTemplateUsed(respuesta, template)

    def test_administracion_carga_su_modulo_javascript(self):
        respuesta = self.client.get(reverse('tienda:administracion'))

        self.assertContains(respuesta, '/static/tienda/js/administracion.js')
        self.assertContains(respuesta, 'data-action="new-product"')
        self.assertContains(respuesta, 'id="admin-product-description"')

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
