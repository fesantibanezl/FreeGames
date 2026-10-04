# FreeGames

Proyecto para la asignatura **Programación Web — Experiencias de Aprendizaje 2 y 3**. FreeGames integra el FrontEnd con Django y Oracle, junto con autenticación, autorización por roles, mantenedores, carrito y pedidos persistentes. Sus recursos REST de categorías y juegos usan token; el sitio incluye un cliente que los consulta sin recargar y una página que consume dos servicios públicos independientes.

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

Para permitir que una aplicación web de **otro origen** consulte las rutas
`/api/` desde el navegador, declara únicamente sus orígenes autorizados antes
de iniciar Django. Por ejemplo, en PowerShell:

```powershell
$env:FREEGAMES_API_ORIGINS = 'http://localhost:3000,http://127.0.0.1:5173'
```

Si esta variable no está definida, no se autoriza ningún origen externo; el
cliente incluido en FreeGames funciona por ser del mismo origen. CORS no
elimina la exigencia del encabezado `Authorization: Token ...` y no habilita
cookies entre sitios. En un despliegue real se deben usar HTTPS y orígenes
concretos de confianza.

## Entregables de base de datos

La entrega incluye archivos independientes para revisar la estructura y los datos sin tener que interpretar las migraciones de Python:

- [`01_estructura_oracle.sql`](base_datos/01_estructura_oracle.sql): DDL de las seis tablas propias, claves, restricciones, índices y relaciones.
- [`02_datos_iniciales.sql`](base_datos/02_datos_iniciales.sql): roles, cuentas, perfiles, cinco categorías y quince juegos mediante operaciones `MERGE` reutilizables.
- [`MER_FreeGames.pdf`](documentacion/MER_FreeGames.pdf): modelo entidad relación normalizado listo para revisión.
- [`MER_FreeGames.md`](documentacion/MER_FreeGames.md): fuente editable del modelo y explicación de las tres formas normales.
- [`PRUEBAS_SEMANA6.md`](documentacion/PRUEBAS_SEMANA6.md): matriz de acceso y comprobaciones funcionales realizadas.
- [`PLAN_SEMANA7.md`](documentacion/PLAN_SEMANA7.md): diseño técnico y avance de las cinco partes de la actividad.
- [`PRUEBAS_SEMANA7.md`](documentacion/PRUEBAS_SEMANA7.md): endpoints, ejemplos, matriz de pruebas y evidencia Git.
- [`PLAN_SEMANA8.md`](documentacion/PLAN_SEMANA8.md): diagnóstico de la rúbrica y avance por partes.
- [`PRUEBAS_SEMANA8.md`](documentacion/PRUEBAS_SEMANA8.md): demostración de las API propias, token, CORS y dos proveedores externos.
- [`crear_entrega_semana8.ps1`](documentacion/crear_entrega_semana8.ps1): crea y verifica el `.zip` con los archivos del proyecto, sin incluir `.git`, `.venv`, la base SQLite local ni secretos en `.env`.

Las instrucciones de ejecución y la relación entre estos scripts y las migraciones se encuentran en [`base_datos/README.md`](base_datos/README.md).

## Preparación de la entrega de Semana 8

Después de revisar los cambios, ejecuta desde PowerShell en la carpeta del
proyecto:

```powershell
.\documentacion\crear_entrega_semana8.ps1
```

Esto genera `FreeGames_Semana8.zip` en la raíz del proyecto y comprueba que
contiene el código, `ENLACE_GITHUB.txt`, `01_estructura_oracle.sql` y
`02_datos_iniciales.sql`. El archivo comprimido se ignora en Git. El script
se detiene si ya existe un `.zip` con ese nombre para evitar sobrescribirlo.
Antes del único envío en AVA, publica el trabajo de Semana 8 en GitHub,
comprueba el enlace del `.txt` y vuelve a generar el comprimido si cambió algún
archivo. La evidencia de contribución grupal debe corresponder a aportes
reales de sus integrantes; no se puede suplir con nombres de autor inventados.

La configuración predeterminada es **solo para desarrollo local**: incluye
`DEBUG`, cuentas y credenciales de demostración y usa HTTP. No publiques esta
configuración ni las cuentas de prueba como un despliegue de producción.

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
- API REST propia para consultar y mantener categorías y juegos mediante JSON.
- Autenticación por token, lectura para usuarios autenticados y escritura exclusiva para administradores.
- Filtros combinables de juegos por nombre, categoría, estado y gratuidad.
- Página `/explorar-api/` que obtiene el token con la contraseña de la cuenta activa y consulta ambas API mediante `fetch()`; el token no se persiste en el almacenamiento del navegador.
- CORS limitado a `/api/` y a los orígenes configurados para aplicaciones web externas.
- Catálogo de FreeToGame integrado mediante `fetch()` sin recargar la página, con filtros, caché y recuperación ante errores.
- Promociones de juegos completos de GamerPower en la misma página Descubrir, con filtro de plataforma, caché, control de ofertas vencidas, manejo de errores y atribución al proveedor.

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
| `/descubrir/` | Catálogo de FreeToGame y ofertas de GamerPower, ambos cargados sin recargar la página. |
| `/explorar-api/` | Cliente autenticado que muestra categorías y filtra juegos desde las API propias, sin recarga. |
| `/servicios/juegos-gratis/` | Adaptador JSON interno para consultar FreeToGame. |
| `/servicios/ofertas-juegos/` | Adaptador JSON interno para consultar GamerPower. |
| `/api/token/` | Obtención de token mediante usuario y contraseña. |
| `/api/categorias/`, `/api/categorias/<id>/` | Colección y detalle REST de categorías. |
| `/api/juegos/`, `/api/juegos/<id>/` | Colección, filtros y detalle REST de juegos. |

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
├── ENLACE_GITHUB.txt          # Repositorio solicitado para la Parte II.
├── api/                       # Serializadores, permisos, vistas y rutas REST.
├── base_datos/                # DDL Oracle y carga de datos iniciales.
├── documentacion/             # MER, planes y matrices de pruebas.
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
└── requirements.txt            # Django, DRF y controlador oficial de Oracle.
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
- Los tokens se almacenan en las tablas de `rest_framework.authtoken`; después de instalar las dependencias debe ejecutarse `python manage.py migrate`.
- La autenticación por token debe publicarse mediante HTTPS fuera del entorno local.
- El token de la página `/explorar-api/` vive solo en la memoria de esa pestaña. Limpiar la página no revoca el token en el servidor; no se debe reutilizar la cuenta de prueba fuera de desarrollo.
- Los dos servicios públicos se consultan desde Django para no depender de CORS de los proveedores ni exponer credenciales en el navegador.
- Las ofertas de GamerPower son externas, temporales y no se agregan al carrito ni alteran el inventario local. La página incluye un enlace activo de atribución al proveedor.

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

## Evidencias de la semana 7

| Criterio | Evidencia en el proyecto |
| --- | --- |
| API REST propia | Aplicación `api`, serializadores y CRUD completo de categorías y juegos. |
| Seguridad | Token DRF, respuesta `401` sin credenciales y escritura restringida al administrador con `403` para clientes. |
| Filtrado | Parámetros `nombre`, `categoria`, `activo` y `gratis` sobre `/api/juegos/`. |
| Servicio REST público | Página `/descubrir/` integrada con FreeToGame mediante `fetch()` sin recarga. |
| Manejo del servicio externo | Validación de parámetros, normalización, caché, enlaces HTTPS, error y reintento. |
| Git | Rama `semana-7` con commits independientes para infraestructura, CRUD, seguridad y consumo externo. |
| Verificación | Matriz completa en `documentacion/PRUEBAS_SEMANA7.md` y pruebas automatizadas de API y servicio externo. |

## Pruebas

Para ejecutar la revisión automatizada:

```powershell
python manage.py check
$env:FREEGAMES_USE_SQLITE = "1"
python manage.py makemigrations --check --dry-run
python manage.py test tienda api
Remove-Item Env:FREEGAMES_USE_SQLITE
python -m pip check
```

Las pruebas automatizadas usan SQLite de manera temporal para poder crear y eliminar su base aislada. La aplicación y las migraciones de desarrollo utilizan Oracle de forma predeterminada.

La suite actual suma **93 pruebas aprobadas**. La matriz de la Semana 6 permanece en [`documentacion/PRUEBAS_SEMANA6.md`](documentacion/PRUEBAS_SEMANA6.md); la evidencia de API REST, seguridad, filtros y consumo externo está en [`documentacion/PRUEBAS_SEMANA7.md`](documentacion/PRUEBAS_SEMANA7.md) y la verificación con Oracle y tres tamaños de pantalla en [`documentacion/PRUEBAS_SEMANA8.md`](documentacion/PRUEBAS_SEMANA8.md).
