# FreeGames

Proyecto para la asignatura **Programación Web — Experiencia de Aprendizaje 2**. En la semana 5, FreeGames incorpora persistencia con Oracle mediante el ORM de Django. El registro y la edición del perfil ya operan desde el Backend; el inicio de sesión y la autorización por roles se completarán en la siguiente parte.

## Cómo ejecutar el proyecto

Se necesita Python 3.10 o una versión posterior y una instancia accesible de Oracle 19c o superior. El entorno de desarrollo utiliza Oracle Database 21c XE con el servicio `XEPDB1`.

Desde PowerShell, ejecuta los siguientes comandos en la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Luego visita `http://127.0.0.1:8000/` en un navegador moderno. Visual Studio Code puede utilizarse para editar el proyecto, pero no es obligatorio.

## Configuración de Oracle

La conexión predeterminada del proyecto está preparada para una instalación local con estos datos:

| Dato | Valor |
| --- | --- |
| Servidor | `localhost` |
| Puerto | `1521` |
| Servicio | `XEPDB1` |
| Usuario | `FREEGAMES` |
| Contraseña | `FreeGames2026` |

El esquema de desarrollo se puede crear desde SQL\*Plus con una cuenta administrativa:

```sql
ALTER SESSION SET CONTAINER = XEPDB1;
CREATE USER FREEGAMES IDENTIFIED BY FreeGames2026;
GRANT CREATE SESSION, CREATE TABLE, CREATE SEQUENCE,
      CREATE PROCEDURE, CREATE TRIGGER TO FREEGAMES;
ALTER USER FREEGAMES QUOTA UNLIMITED ON USERS;
```

Luego se comprueba la conexión y se crean las tablas internas de Django con:

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py check
```

La configuración admite reemplazar los valores locales mediante las variables `FREEGAMES_DB_NAME`, `FREEGAMES_DB_USER` y `FREEGAMES_DB_PASSWORD`. Para ejecutar comprobaciones sin Oracle puede definirse temporalmente `FREEGAMES_USE_SQLITE=1`.

## Funcionalidades implementadas

- Catálogo inicial con cinco categorías y quince videojuegos, ampliable desde el mantenedor.
- Navegación adaptable con menú colapsable en pantallas pequeñas.
- Registro y edición de perfil persistentes en Oracle, con validaciones en el servidor.
- Inicio de sesión y recuperación todavía demostrativos hasta completar la autenticación Django.
- Validación inmediata de datos y mensajes accesibles en los formularios.
- Roles de **cliente** y **administrador** con vistas y permisos diferentes.
- Carrito con cantidades, total, disponibilidad y compra simulada sin cobro real.
- Historial de pedidos para el cliente.
- Panel administrativo para registrar y modificar juegos, controlar su publicación y administrar roles y estados de cuentas.
- Vistas, plantillas y archivos estáticos organizados mediante Django.
- Modelos persistentes para roles y perfiles de usuario, visibles desde Django Admin.

## Rutas principales

| Ruta | Propósito |
| --- | --- |
| `/` | Página inicial y acceso a categorías. |
| `/accion/`, `/aventura/`, `/deportes/`, `/carreras/`, `/estrategia/` | Catálogo por categoría. |
| `/registro/` | Registro de una cuenta de cliente. |
| `/login/` | Inicio de sesión. |
| `/recuperar-clave/` | Recuperación simulada de contraseña. |
| `/perfil/` | Consulta y edición del perfil activo. |
| `/carrito/` | Carrito y confirmación de una compra simulada. |
| `/mis-compras/` | Historial exclusivo del rol cliente. |
| `/administracion/` | Panel exclusivo del rol administrador. |
| `/admin/` | Administrador de Django para usuarios, perfiles y roles. |

## Cuentas de prueba

Las migraciones crean estas cuentas en Oracle para revisar los roles y funcionalidades del proyecto. Las credenciales no se muestran dentro del formulario de inicio de sesión.

| Rol | Usuario | Contraseña |
| --- | --- | --- |
| Cliente | `cliente` | `Cliente#2026` |
| Administrador | `admin` | `Admin#2026` |

La cuenta `admin` ya permite ingresar a `/admin/` mediante la autenticación de Django. El registro crea cuentas nuevas en Oracle e inicia su sesión para acceder al perfil. Hasta completar la siguiente parte, el formulario `/login/` continúa usando la demostración FrontEnd de la semana 4.

## Estructura del proyecto

```text
FreeGames/
├── freegames/                 # Configuración y rutas principales de Django.
├── tienda/
│   ├── static/tienda/
│   │   ├── css/               # Estilos y diseño adaptable.
│   │   ├── img/               # Ilustraciones PNG del catálogo.
│   │   └── js/                # Funcionalidad FrontEnd y datos simulados.
│   ├── templates/tienda/      # Plantilla base y páginas de la aplicación.
│   ├── catalogo.py            # Categorías y contenido de presentación.
│   ├── forms.py               # Registro y actualización segura del perfil.
│   ├── models.py              # Roles y perfiles persistentes de usuario.
│   ├── admin.py               # Configuración de los modelos en Django Admin.
│   ├── migrations/            # Estructura y datos iniciales de Oracle.
│   ├── tests.py               # Pruebas de vistas, rutas y plantillas.
│   ├── urls.py                # Rutas de la aplicación tienda.
│   └── views.py               # Vistas que renderizan las plantillas.
├── manage.py
└── requirements.txt            # Django y controlador oficial de Oracle.
```

## Flujo de una solicitud en Django

Por ejemplo, al visitar `/accion/` ocurre el siguiente recorrido:

```text
Navegador
  → freegames/urls.py
  → tienda/urls.py
  → views.categoria
  → contexto definido en catalogo.py
  → templates/tienda/categoria.html
  → templates/tienda/base.html y static/tienda/
  → respuesta HTML
```

La plantilla base concentra la navegación, los estilos y los módulos JavaScript compartidos. Las vistas preparan el contexto y seleccionan la plantilla, mientras que las rutas nombradas permiten navegar sin depender de archivos HTML físicos.

## Consideraciones

- Oracle está configurado como base de datos predeterminada y contiene las tablas internas de Django después de ejecutar las migraciones.
- El registro y la modificación del perfil utilizan Oracle; las contraseñas se almacenan mediante el sistema seguro de Django.
- El formulario manual de inicio de sesión, el carrito y las compras todavía utilizan `localStorage`; su integración se realizará por partes durante la semana 5.
- Los juegos creados desde el mantenedor usan la imagen representativa de la categoría seleccionada.
- Si `localStorage` no está disponible, se usa memoria mientras la página permanezca abierta.
- Las contraseñas y la compra son demostrativas. No existe un cobro real ni una integración con WebPay.
- La interfaz considera navegación por teclado, foco visible, enlace para saltar al contenido y adaptación a móvil, tableta y escritorio.
- El usuario estándar de Django almacena las credenciales; `PerfilUsuario` incorpora rol, fecha de nacimiento y dirección.
- Los roles iniciales son **Cliente** y **Administrador**. Un rol asociado a perfiles no puede eliminarse accidentalmente.

## Evidencias de la semana 4

| Criterio | Evidencia en el proyecto |
| --- | --- |
| Aplicación creada con Django | Proyecto `freegames`, aplicación `tienda` y `manage.py`. |
| Configuración interna | `TiendaConfig` registrada en `settings.py`; rutas separadas en los dos archivos `urls.py`; vistas en `tienda/views.py`. |
| Migración de directorios | HTML en `templates/tienda` y CSS, JavaScript e imágenes en `static/tienda`. |
| Visualización local | Ejecución con `python manage.py runserver` y rutas HTTP comprobadas. |
| Continuidad en Git | Desarrollo incremental en la rama `semana-4`, mediante commits separados por parte. |

## Pruebas

Para ejecutar la revisión automatizada:

```powershell
python manage.py check
$env:FREEGAMES_USE_SQLITE = "1"
python manage.py test tienda
Remove-Item Env:FREEGAMES_USE_SQLITE
```

Las pruebas automatizadas usan SQLite de manera temporal para poder crear y eliminar su base aislada. La aplicación y las migraciones de desarrollo utilizan Oracle de forma predeterminada.

También se revisaron manualmente el registro, la recuperación, los dos roles, las restricciones de acceso, el perfil, el carrito, la compra simulada, el historial y el panel administrativo.
