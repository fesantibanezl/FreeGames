# Plan técnico de la Semana 7

## Objetivo

La Semana 7 incorporará una API REST propia y segura en FreeGames, además del
consumo asincrónico de un servicio REST público. La implementación conservará
las funciones y pruebas aprobadas hasta la Semana 6.

## Modelos que publicará la API

- `Categoria`: recurso utilizado para organizar el catálogo.
- `Juego`: recurso principal que podrá consultarse y mantenerse mediante la
  API.

No se publicarán contraseñas, perfiles, pedidos ni datos personales de los
usuarios.

## Rutas planificadas

| Método | Ruta | Propósito |
| --- | --- | --- |
| `POST` | `/api/token/` | Obtener un token con credenciales válidas. |
| `GET`, `POST` | `/api/categorias/` | Listar o crear categorías. |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/categorias/<id>/` | Consultar o mantener una categoría. |
| `GET`, `POST` | `/api/juegos/` | Listar o crear juegos. |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/juegos/<id>/` | Consultar o mantener un juego. |

## Seguridad planificada

- Toda solicitud a los recursos propios requerirá un token válido.
- Los usuarios autenticados podrán consultar categorías y juegos.
- Las operaciones de escritura se limitarán a administradores.
- El endpoint de obtención de token será la única excepción pública de la API
  propia.
- La configuración global usa denegación por defecto para evitar publicar una
  vista nueva accidentalmente.

## Filtros planificados

La colección de juegos aceptará filtros por nombre, categoría, estado y
gratuidad. Los parámetros previstos son `nombre`, `categoria`, `activo` y
`gratis`.

## Dependencias

- Django REST Framework se incorpora sobre Django 5.2.
- `rest_framework.authtoken` administrará los tokens persistentes.
- Se conserva `oracledb`, el controlador actual y oficial usado por FreeGames.
- Pillow no es necesario porque las imágenes del catálogo se almacenan como
  rutas estáticas en campos de texto, no mediante `ImageField`.
- `cx_Oracle` corresponde al proyecto Hsc de referencia y no reemplazará el
  controlador actual.

## División del desarrollo

1. Preparar y comprobar la infraestructura.
2. Construir serializers y CRUD REST.
3. Incorporar token, permisos y filtros.
4. Consumir un servicio REST público sin recargar la página.
5. Completar pruebas, documentación y evidencia Git.

## Estado de la Parte 1

- Rama local `semana-7` creada.
- Base de Semana 6 comprobada con 38 pruebas aprobadas.
- Aplicación `api` creada y separada de `tienda`.
- Rutas base y configuración restrictiva preparadas.
- Migraciones de `authtoken` verificadas al crear la base temporal de pruebas.
  Su aplicación sobre Oracle se realizará con `python manage.py migrate` en el
  entorno que tenga disponible la instancia del proyecto.
- No se han implementado aún serializers, endpoints de datos ni consumo
  externo.
