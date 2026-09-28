from django.conf import settings
from django.test import SimpleTestCase


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
