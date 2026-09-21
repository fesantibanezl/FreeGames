from django.test import SimpleTestCase
from django.urls import reverse


class CatalogoViewsTests(SimpleTestCase):
    def test_inicio_muestra_las_cinco_categorias_y_recursos_estaticos(self):
        respuesta = self.client.get(reverse('tienda:inicio'))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'class="category-row', count=5)
        self.assertContains(respuesta, '/static/tienda/css/style.css')

    def test_cada_categoria_muestra_sus_tres_juegos(self):
        for slug in ('accion', 'aventura', 'deportes', 'carreras', 'estrategia'):
            with self.subTest(slug=slug):
                respuesta = self.client.get(reverse('tienda:categoria', kwargs={'slug': slug}))

                self.assertEqual(respuesta.status_code, 200)
                self.assertContains(respuesta, 'class="game-card"', count=3)

    def test_categoria_desconocida_responde_404(self):
        respuesta = self.client.get(reverse('tienda:categoria', kwargs={'slug': 'desconocida'}))

        self.assertEqual(respuesta.status_code, 404)

    def test_paginas_funcionales_renderizan_sus_contenedores(self):
        rutas_y_contenedores = {
            'carrito': 'id="cart-page"',
            'login': 'id="login-form"',
            'registro': 'id="registro-form"',
            'recuperar_clave': 'id="recuperar-form"',
            'perfil': 'id="perfil-form"',
            'mis_compras': 'id="history-content"',
            'compra_exitosa': 'id="purchase-result"',
            'administracion': 'id="administration-content"',
        }

        for nombre_ruta, contenedor in rutas_y_contenedores.items():
            with self.subTest(nombre_ruta=nombre_ruta):
                respuesta = self.client.get(reverse(f'tienda:{nombre_ruta}'))

                self.assertEqual(respuesta.status_code, 200)
                self.assertContains(respuesta, contenedor)

    def test_administracion_carga_su_modulo_javascript(self):
        respuesta = self.client.get(reverse('tienda:administracion'))

        self.assertContains(respuesta, '/static/tienda/js/administracion.js')
        self.assertContains(respuesta, 'data-action="new-product"')
        self.assertContains(respuesta, 'id="admin-product-description"')

    def test_categoria_expone_la_grilla_para_el_catalogo_guardado(self):
        respuesta = self.client.get(reverse('tienda:categoria', kwargs={'slug': 'accion'}))

        self.assertContains(respuesta, 'data-products-grid')
