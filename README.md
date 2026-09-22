# FreeGames

Proyecto para la asignatura **Programación Web — Experiencia de Aprendizaje 2**. FreeGames integra el FrontEnd con Django y Oracle, junto con autenticación, autorización por roles, mantenedores, carrito y pedidos persistentes. En la semana 6 se completa la gestión de cuentas y la recuperación segura de contraseñas.

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

## Entregables de base de datos

La entrega incluye archivos independientes para revisar la estructura y los datos sin tener que interpretar las migraciones de Python:

- [`01_estructura_oracle.sql`](base_datos/01_estructura_oracle.sql): DDL de las seis tablas propias, claves, restricciones, índices y relaciones.
- [`02_datos_iniciales.sql`](base_datos/02_datos_iniciales.sql): roles, cuentas, perfiles, cinco categorías y quince juegos mediante operaciones `MERGE` reutilizables.
- [`MER_FreeGames.pdf`](documentacion/MER_FreeGames.pdf): modelo entidad relación normalizado listo para revisión.
- [`MER_FreeGames.md`](documentacion/MER_FreeGames.md): fuente editable del modelo y explicación de las tres formas normales.

Las instrucciones de ejecución y la relación entre estos scripts y las migraciones se encuentran en [`base_datos/README.md`](base_datos/README.md).

## Funcionalidades implementadas

- Catálogo persistente con cinco categorías y quince videojuegos iniciales, ampliable desde el mantenedor.
- Navegación adaptable con menú colapsable en pantallas pequeñas.
- Registro, inicio de sesión por usuario o correo y edición de perfil persistentes en Oracle.
- Recuperación de contraseña mediante un enlace temporal de un solo uso generado por Django.
- Sesiones seguras de Django, cierre de sesión por `POST` y validaciones en el servidor.
- Validación inmediata de datos y mensajes accesibles en los formularios.
- Roles de **cliente** y **administrador** con navegación, redirecciones y rutas protegidas diferentes.
- Carrito guardado en la sesión Django, con cantidades, total y validación de disponibilidad.
- Compra transaccional que registra el pedido y su detalle en Oracle y descuenta el stock.
- Historial persistente de pedidos para cada cliente.
- CRUD completo de juegos para crear, consultar, modificar y eliminar registros desde la interfaz.
- CRUD de usuarios desde el panel administrativo para crear, consultar, modificar y eliminar cuentas.
- Conservación de las cuentas asociadas a compras: al intentar eliminarlas se desactivan para proteger el historial.
- Vistas, plantillas y archivos estáticos organizados mediante Django.
- Modelos persistentes para categorías, juegos, pedidos, detalles, roles y perfiles, visibles desde Django Admin.

## Rutas principales

| Ruta | Propósito |
| --- | --- |
| `/` | Página inicial y acceso a categorías. |
| `/accion/`, `/aventura/`, `/deportes/`, `/carreras/`, `/estrategia/` | Catálogo por categoría. |
| `/registro/` | Registro de una cuenta de cliente. |
| `/login/` | Inicio de sesión. |
| `/logout/` | Cierre seguro de la sesión activa mediante `POST`. |
| `/recuperar-clave/` | Solicitud de un enlace temporal para definir una contraseña nueva. |
| `/perfil/` | Consulta y edición del perfil activo. |
| `/carrito/` | Carrito de sesión y confirmación de una compra simulada. |
| `/mis-compras/` | Historial persistente exclusivo del rol cliente. |
| `/administracion/` | CRUD y mantenedores exclusivos del administrador. |
| `/admin/` | Administrador Django para todos los modelos persistentes. |

## Cuentas de prueba

Las migraciones crean estas cuentas en Oracle para revisar los roles y funcionalidades del proyecto. Las credenciales no se muestran dentro del formulario de inicio de sesión.

| Rol | Usuario | Contraseña |
| --- | --- | --- |
| Cliente | `cliente` | `Cliente#2026` |
| Administrador | `admin` | `Admin#2026` |

Ambas cuentas permiten ingresar desde `/login/` con el nombre de usuario o el correo electrónico. La cuenta `admin` también permite ingresar a `/admin/`. El registro crea cuentas nuevas de cliente en Oracle e inicia su sesión para acceder al perfil.

El cliente puede visitar el catálogo, el perfil, el carrito y su historial. El administrador es dirigido al mantenedor y no puede entrar a las páginas internas del cliente. Las rutas protegidas envían a `/login/` a quien aún no ha iniciado sesión.

Durante el desarrollo local, los mensajes de recuperación se imprimen en la terminal donde se ejecuta `runserver`. El enlace vence después de una hora y queda invalidado al cambiar la contraseña. La variable `FREEGAMES_EMAIL_BACKEND` permite reemplazar este comportamiento por un servicio de correo configurado.

## Estructura del proyecto

```text
FreeGames/
├── base_datos/                # DDL Oracle y carga de datos iniciales.
├── documentacion/             # MER normalizado en PDF y formato editable.
├── freegames/                 # Configuración y rutas principales de Django.
├── tienda/
│   ├── static/tienda/
│   │   ├── css/               # Estilos y diseño adaptable.
│   │   ├── img/               # Ilustraciones PNG del catálogo.
│   │   └── js/                # Validaciones complementarias del navegador.
│   ├── templates/tienda/      # Plantilla base y páginas de la aplicación.
│   ├── context_processors.py  # Rol disponible en todas las plantillas.
│   ├── decorators.py          # Restricciones de acceso por rol.
│   ├── forms.py               # Formularios de cuentas, perfil y mantenedores.
│   ├── models.py              # Catálogo, pedidos, roles y perfiles persistentes.
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
  → Categoria y Juego mediante el ORM
  → Oracle
  → templates/tienda/categoria.html
  → templates/tienda/base.html y static/tienda/
  → respuesta HTML
```

La plantilla base concentra la navegación, los estilos y los módulos JavaScript compartidos. Las vistas preparan el contexto y seleccionan la plantilla, mientras que las rutas nombradas permiten navegar sin depender de archivos HTML físicos.

## Consideraciones

- Oracle está configurado como base de datos predeterminada y contiene las tablas internas de Django después de ejecutar las migraciones.
- El registro, la autenticación, los perfiles, el catálogo, los pedidos y los mantenedores utilizan Django y Oracle.
- Las contraseñas se almacenan mediante el sistema seguro de Django y nunca se guardan en el navegador.
- El carrito utiliza la sesión Django y deja de depender de `localStorage`.
- Los juegos creados desde el mantenedor usan la imagen representativa de la categoría seleccionada.
- Las contraseñas se validan con el sistema de autenticación de Django. La compra sigue siendo demostrativa; no existe un cobro real ni una integración con WebPay.
- La interfaz considera navegación por teclado, foco visible, enlace para saltar al contenido y adaptación a móvil, tableta y escritorio.
- El usuario estándar de Django almacena las credenciales; `PerfilUsuario` incorpora rol, fecha de nacimiento y dirección.
- Los roles iniciales son **Cliente** y **Administrador**. Un rol asociado a perfiles no puede eliminarse accidentalmente.
- Los juegos asociados a pedidos no se eliminan para conservar la integridad del historial; el mantenedor los oculta del catálogo.

## Evidencias de la semana 4

| Criterio | Evidencia en el proyecto |
| --- | --- |
| Aplicación creada con Django | Proyecto `freegames`, aplicación `tienda` y `manage.py`. |
| Configuración interna | `TiendaConfig` registrada en `settings.py`; rutas separadas en los dos archivos `urls.py`; vistas en `tienda/views.py`. |
| Migración de directorios | HTML en `templates/tienda` y CSS, JavaScript e imágenes en `static/tienda`. |
| Visualización local | Ejecución con `python manage.py runserver` y rutas HTTP comprobadas. |
| Continuidad en Git | Desarrollo incremental en la rama `semana-4`, mediante commits separados por parte. |

## Evidencias de la semana 5

| Criterio | Evidencia en el proyecto |
| --- | --- |
| Conexión con Oracle | Configuración en `settings.py`, controlador `oracledb` y migraciones aplicadas en `XEPDB1`. |
| Modelos persistentes | Categorías, juegos, pedidos, detalles, roles y perfiles definidos mediante el ORM. |
| CRUD completo | El mantenedor permite crear, leer, actualizar, ocultar y eliminar juegos desde la interfaz. |
| Operaciones DML | El catálogo consulta Oracle; las compras crean pedidos, crean detalles y actualizan existencias. |
| Administración de usuarios | El administrador crea, consulta, modifica y elimina cuentas persistentes. |
| Autenticación y autorización | Sesiones Django, cierre por `POST` y rutas restringidas para cliente y administrador. |

## Evidencias de la semana 6

| Criterio | Evidencia en el proyecto |
| --- | --- |
| Seguridad de acceso | Rutas limitadas por método HTTP, sesión y rol; formularios protegidos con CSRF. |
| Gestión de cuentas | CRUD completo de usuarios y protección del administrador y del historial de pedidos. |
| Recuperación de contraseña | Flujo Django con token temporal, respuesta que no revela cuentas y validaciones de seguridad. |
| Modelo Oracle | Seis tablas propias relacionadas con `AUTH_USER`, migraciones sincronizadas y conexión real comprobada. |
| Entregables de datos | Script DDL, script idempotente de datos iniciales y MER normalizado. |
| Verificación | Pruebas automatizadas de catálogo, cuentas, permisos, carrito, pedidos y mantenedores. |

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
