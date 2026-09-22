from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.db.models.deletion import ProtectedError
from django.test import SimpleTestCase, TestCase
from django.urls import resolve, reverse

from . import views
from .models import (
    Categoria,
    DetallePedido,
    Juego,
    Pedido,
    PerfilUsuario,
    Rol,
)


class CatalogoViewsTests(TestCase):
    def test_inicio_muestra_las_cinco_categorias_persistentes(self):
        respuesta = self.client.get(reverse('tienda:inicio'))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'class="category-row', count=5)
        self.assertContains(respuesta, '/static/tienda/css/style.css')
        self.assertTemplateUsed(respuesta, 'tienda/index.html')

    def test_cada_categoria_muestra_sus_tres_juegos_publicados(self):
        for slug in ('accion', 'aventura', 'deportes', 'carreras', 'estrategia'):
            with self.subTest(slug=slug):
                respuesta = self.client.get(
                    reverse('tienda:categoria', kwargs={'slug': slug}),
                )

                self.assertEqual(respuesta.status_code, 200)
                self.assertContains(respuesta, 'class="game-card"', count=3)
                self.assertTemplateUsed(respuesta, 'tienda/categoria.html')

    def test_categoria_no_muestra_juegos_ocultos(self):
        juego = Juego.objects.get(slug='call-of-duty')
        juego.activo = False
        juego.save(update_fields=('activo',))

        respuesta = self.client.get(
            reverse('tienda:categoria', kwargs={'slug': 'accion'}),
        )

        self.assertContains(respuesta, 'class="game-card"', count=2)
        self.assertNotContains(respuesta, 'Call of Duty')

    def test_categoria_desconocida_responde_404(self):
        respuesta = self.client.get(
            reverse('tienda:categoria', kwargs={'slug': 'desconocida'}),
        )
        self.assertEqual(respuesta.status_code, 404)

    def test_paginas_publicas_renderizan_sus_contenedores(self):
        rutas = {
            'login': ('id="login-form"', 'tienda/login.html'),
            'registro': ('id="registro-form"', 'tienda/registro.html'),
            'recuperar_clave': (
                'id="recuperar-form"',
                'tienda/recuperar_clave.html',
            ),
        }

        for nombre_ruta, (contenedor, template) in rutas.items():
            with self.subTest(nombre_ruta=nombre_ruta):
                respuesta = self.client.get(reverse(f'tienda:{nombre_ruta}'))
                self.assertEqual(respuesta.status_code, 200)
                self.assertContains(respuesta, contenedor)
                self.assertTemplateUsed(respuesta, template)


class ConfiguracionDjangoTests(SimpleTestCase):
    def test_tienda_esta_registrada_y_sus_rutas_resuelven_vistas(self):
        self.assertIn('tienda.apps.TiendaConfig', settings.INSTALLED_APPS)
        self.assertIs(resolve('/').func, views.inicio)
        self.assertIs(resolve('/accion/').func, views.categoria)
        self.assertIs(resolve('/administracion/').func, views.administracion)
        self.assertIs(
            resolve('/administracion/juegos/guardar/').func,
            views.guardar_juego,
        )

    def test_django_encuentra_los_recursos_estaticos_principales(self):
        recursos = (
            'tienda/css/style.css',
            'tienda/js/validaciones.js',
            'tienda/js/autenticacion.js',
            'tienda/img/accion.png',
        )

        for recurso in recursos:
            with self.subTest(recurso=recurso):
                self.assertIsNotNone(finders.find(recurso))


class ModelosPersistenciaTests(TestCase):
    def test_migraciones_crean_roles_catalogo_y_cuentas_iniciales(self):
        self.assertEqual(
            set(Rol.objects.values_list('codigo', flat=True)),
            {Rol.Codigos.CLIENTE, Rol.Codigos.ADMINISTRADOR},
        )
        self.assertEqual(Categoria.objects.count(), 5)
        self.assertEqual(Juego.objects.count(), 15)

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

    def test_relaciones_en_uso_estan_protegidas(self):
        rol_cliente = Rol.objects.get(codigo=Rol.Codigos.CLIENTE)
        with self.assertRaises(ProtectedError):
            rol_cliente.delete()

        categoria = Categoria.objects.get(slug='accion')
        with self.assertRaises(ProtectedError):
            categoria.delete()


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
        usuario = get_user_model().objects.select_related('perfil__rol').get(
            username='alexgamer',
        )
        self.assertTrue(usuario.check_password('Clave#Segura2026'))
        self.assertNotEqual(usuario.password, 'Clave#Segura2026')
        self.assertEqual(usuario.perfil.rol.codigo, Rol.Codigos.CLIENTE)
        self.assertEqual(int(self.client.session['_auth_user_id']), usuario.pk)

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
        self.assertContains(respuesta, 'Ese nombre de usuario ya está registrado.')
        self.assertContains(
            respuesta,
            'Ese correo electrónico ya está registrado.',
        )

    def test_perfil_requiere_usuario_autenticado(self):
        respuesta = self.client.get(reverse('tienda:perfil'))
        self.assertRedirects(
            respuesta,
            f"{reverse('tienda:login')}?next={reverse('tienda:perfil')}",
            fetch_redirect_response=False,
        )

    def test_perfil_muestra_y_modifica_los_datos_persistentes(self):
        usuario = get_user_model().objects.get(username='cliente')
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
        self.assertRedirects(respuesta, reverse('tienda:administracion'))

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
        self.assertContains(
            respuesta,
            'La cuenta está desactivada. Contacta al administrador.',
        )

    def test_logout_solo_acepta_post_y_elimina_la_sesion(self):
        self.client.force_login(self.cliente)
        self.assertEqual(
            self.client.get(reverse('tienda:logout')).status_code,
            405,
        )

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

    def test_administrador_accede_al_crud_y_no_al_area_cliente(self):
        self.client.force_login(self.administrador)
        respuesta = self.client.get(reverse('tienda:administracion'))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'CRUD persistente')
        self.assertContains(respuesta, 'id="admin-product-description"')
        self.assertContains(respuesta, 'Juegos registrados en Oracle')

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

    def test_navegacion_se_adapta_a_la_sesion_y_al_rol(self):
        respuesta = self.client.get(reverse('tienda:inicio'))
        self.assertContains(respuesta, 'Iniciar sesión')
        self.assertNotContains(respuesta, 'Cerrar sesión')

        self.client.force_login(self.cliente)
        respuesta = self.client.get(reverse('tienda:inicio'))
        self.assertContains(respuesta, 'Mi perfil: cliente')
        self.assertContains(respuesta, 'Mis compras')
        self.assertContains(respuesta, 'Cerrar sesión')
        self.assertNotContains(respuesta, '>Administración</a>')

        self.client.force_login(self.administrador)
        respuesta = self.client.get(reverse('tienda:administracion'))
        self.assertContains(respuesta, '>Administración</a>')
        self.assertNotContains(respuesta, '>Acción</a>')


class CrudJuegosYUsuariosTests(TestCase):
    def setUp(self):
        Usuario = get_user_model()
        self.administrador = Usuario.objects.get(username='admin')
        self.cliente = Usuario.objects.get(username='cliente')
        self.categoria = Categoria.objects.get(slug='accion')
        self.client.force_login(self.administrador)

    def datos_juego(self, **cambios):
        datos = {
            'nombre': 'Hollow Knight',
            'categoria': self.categoria.pk,
            'descripcion': 'Una aventura persistente creada desde el mantenedor.',
            'precio': 12990,
            'stock': 11,
            'activo': 'on',
        }
        datos.update(cambios)
        return datos

    def test_crud_completo_de_juegos_modifica_la_base_de_datos(self):
        respuesta = self.client.post(
            reverse('tienda:guardar_juego'),
            self.datos_juego(),
        )
        self.assertEqual(respuesta.status_code, 302)
        juego = Juego.objects.get(nombre='Hollow Knight')

        self.client.logout()
        respuesta = self.client.get(
            reverse('tienda:categoria', kwargs={'slug': 'accion'}),
        )
        self.assertContains(respuesta, 'Hollow Knight')

        self.client.force_login(self.administrador)
        self.client.post(
            reverse('tienda:guardar_juego'),
            self.datos_juego(
                juego_id=juego.pk,
                nombre='Hollow Knight Edición Completa',
                stock=20,
            ),
        )
        juego.refresh_from_db()
        self.assertEqual(juego.nombre, 'Hollow Knight Edición Completa')
        self.assertEqual(juego.stock, 20)

        self.client.post(
            reverse('tienda:cambiar_estado_juego', args=(juego.pk,)),
        )
        juego.refresh_from_db()
        self.assertFalse(juego.activo)

        self.client.post(
            reverse('tienda:eliminar_juego', args=(juego.pk,)),
        )
        self.assertFalse(Juego.objects.filter(pk=juego.pk).exists())

    def test_formulario_rechaza_nombre_de_juego_duplicado(self):
        respuesta = self.client.post(
            reverse('tienda:guardar_juego'),
            self.datos_juego(nombre='CALL OF DUTY'),
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta,
            'Ya existe un juego registrado con ese nombre.',
        )
        self.assertEqual(Juego.objects.filter(nombre__iexact='call of duty').count(), 1)

    def test_operaciones_administrativas_rechazan_al_cliente(self):
        self.client.force_login(self.cliente)
        respuesta = self.client.post(
            reverse('tienda:guardar_juego'),
            self.datos_juego(),
        )

        self.assertRedirects(respuesta, reverse('tienda:inicio'))
        self.assertFalse(Juego.objects.filter(nombre='Hollow Knight').exists())

    def test_administrador_modifica_rol_y_estado_de_otra_cuenta(self):
        respuesta = self.client.post(
            reverse('tienda:actualizar_usuario', args=(self.cliente.pk,)),
            {'rol': Rol.Codigos.ADMINISTRADOR, 'activo': 'false'},
        )

        self.assertEqual(respuesta.status_code, 302)
        self.cliente.refresh_from_db()
        self.cliente.perfil.refresh_from_db()
        self.assertFalse(self.cliente.is_active)
        self.assertTrue(self.cliente.is_staff)
        self.assertEqual(
            self.cliente.perfil.rol.codigo,
            Rol.Codigos.ADMINISTRADOR,
        )

    def test_administrador_no_puede_desactivar_su_propia_cuenta(self):
        respuesta = self.client.post(
            reverse('tienda:actualizar_usuario', args=(self.administrador.pk,)),
            {'rol': Rol.Codigos.CLIENTE, 'activo': 'false'},
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta,
            'No puedes cambiar tu propio rol ni desactivar tu cuenta.',
        )
        self.administrador.refresh_from_db()
        self.assertTrue(self.administrador.is_active)
        self.assertTrue(self.administrador.is_staff)


class CarritoYPedidosTests(TestCase):
    def setUp(self):
        Usuario = get_user_model()
        self.cliente = Usuario.objects.get(username='cliente')
        self.administrador = Usuario.objects.get(username='admin')
        self.juego = Juego.objects.get(slug='call-of-duty')
        self.client.force_login(self.cliente)

    def test_carrito_se_guarda_en_sesion_y_permite_actualizar_y_quitar(self):
        self.client.post(
            reverse('tienda:agregar_carrito', args=(self.juego.pk,)),
        )
        self.assertEqual(
            self.client.session['freegames_carrito'][str(self.juego.pk)],
            1,
        )

        self.client.post(
            reverse('tienda:actualizar_carrito', args=(self.juego.pk,)),
            {'cantidad': 2},
        )
        respuesta = self.client.get(reverse('tienda:carrito'))
        self.assertContains(respuesta, 'value="2"')
        self.assertContains(respuesta, '$39.980')

        self.client.post(
            reverse('tienda:quitar_carrito', args=(self.juego.pk,)),
        )
        self.assertNotIn(str(self.juego.pk), self.client.session['freegames_carrito'])

    def test_finalizar_compra_crea_pedido_detalle_y_descuenta_stock(self):
        stock_inicial = self.juego.stock
        self.client.post(
            reverse('tienda:agregar_carrito', args=(self.juego.pk,)),
        )
        self.client.post(
            reverse('tienda:actualizar_carrito', args=(self.juego.pk,)),
            {'cantidad': 2},
        )

        respuesta = self.client.post(reverse('tienda:finalizar_compra'))

        self.assertEqual(respuesta.status_code, 302)
        pedido = Pedido.objects.get(usuario=self.cliente)
        detalle = DetallePedido.objects.get(pedido=pedido)
        self.assertEqual(detalle.juego, self.juego)
        self.assertEqual(detalle.cantidad, 2)
        self.assertEqual(pedido.total, self.juego.precio * 2)
        self.juego.refresh_from_db()
        self.assertEqual(self.juego.stock, stock_inicial - 2)
        self.assertEqual(self.client.session['freegames_carrito'], {})

        comprobante = self.client.get(respuesta.headers['Location'])
        self.assertContains(comprobante, pedido.codigo)
        historial = self.client.get(reverse('tienda:mis_compras'))
        self.assertContains(historial, pedido.codigo)
        self.assertContains(historial, self.juego.nombre)

    def test_compra_rechaza_cantidad_superior_al_stock(self):
        sesion = self.client.session
        sesion['freegames_carrito'] = {str(self.juego.pk): self.juego.stock + 1}
        sesion.save()

        respuesta = self.client.post(reverse('tienda:finalizar_compra'))

        self.assertRedirects(respuesta, reverse('tienda:carrito'))
        self.assertFalse(Pedido.objects.filter(usuario=self.cliente).exists())

    def test_juego_comprado_no_se_elimina_y_queda_oculto(self):
        self.client.post(
            reverse('tienda:agregar_carrito', args=(self.juego.pk,)),
        )
        self.client.post(reverse('tienda:finalizar_compra'))

        self.client.force_login(self.administrador)
        self.client.post(
            reverse('tienda:eliminar_juego', args=(self.juego.pk,)),
        )
        self.juego.refresh_from_db()
        self.assertFalse(self.juego.activo)

    def test_un_cliente_no_puede_ver_el_comprobante_de_otro(self):
        pedido = Pedido.objects.create(
            usuario=self.cliente,
            codigo='FG-PRIVADO',
            total=1000,
        )
        otro = get_user_model().objects.create_user(
            username='otrocliente',
            password='Clave#2026',
        )
        PerfilUsuario.objects.create(
            usuario=otro,
            rol=Rol.objects.get(codigo=Rol.Codigos.CLIENTE),
        )
        self.client.force_login(otro)

        respuesta = self.client.get(
            f"{reverse('tienda:compra_exitosa')}?pedido={pedido.pk}",
        )
        self.assertEqual(respuesta.status_code, 404)
