# Semana 8 — evidencia de las partes 2, 3 y 4

## Dos recursos REST propios

| Recurso | Colección y detalle | Lectura | Escritura |
| --- | --- | --- | --- |
| Categorías | `/api/categorias/` y `/api/categorias/<id>/` | Token de cliente o administrador | Token de administrador |
| Juegos | `/api/juegos/` y `/api/juegos/<id>/` | Token de cliente o administrador; filtros combinables | Token de administrador |

Ambos recursos admiten operaciones CRUD y respuestas JSON. Los filtros de
`GET /api/juegos/` son `nombre`, `categoria`, `activo` y `gratis`. Se obtiene
un token mediante `POST /api/token/` y se envía en cada solicitud protegida:

```text
Authorization: Token CODIGO_DEL_TOKEN
```

La página interna `/explorar-api/` permite comprobar el flujo completo: el
usuario inicia sesión en FreeGames, confirma su contraseña, obtiene un token,
consulta categorías para completar el selector y consulta juegos con filtros
mediante `fetch()`. Los resultados cambian sin recargar. El token permanece
solo en una variable de JavaScript de la pestaña; no aparece en HTML ni se
guarda en `localStorage` o `sessionStorage`. El botón para limpiar el acceso
descarta la copia del token en la página, **no lo revoca en el servidor**.

## Consumo desde otro origen

`django-cors-headers` permite preflight y respuestas CORS exclusivamente bajo
`/api/`. La variable de entorno `FREEGAMES_API_ORIGINS` contiene una lista
separada por comas de orígenes autorizados, por ejemplo:

```powershell
$env:FREEGAMES_API_ORIGINS = 'http://localhost:3000'
```

Sin esta variable la lista queda vacía. CORS no sustituye la autenticación:
una consulta sin token sigue devolviendo HTTP 401 aunque el origen esté
autorizado. No se permiten cookies entre sitios. Un cliente de servidor,
Postman o ARC puede consultar la API con token sin depender de CORS.

## Comprobaciones automatizadas

En el entorno de desarrollo, con SQLite aislado de Oracle:

```powershell
$env:FREEGAMES_USE_SQLITE = '1'
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test api tienda
node --check tienda\static\tienda\js\explorar_api.js
```

Resultado de la parte 2: `manage.py check` sin problemas, **83
pruebas correctas** y JavaScript sin errores de sintaxis. Las pruebas nuevas
incluyen acceso sin token e inválido a ambas API, uso real de un token obtenido
en `/api/token/`, verificación de que la sesión web no sustituye al token,
denegación de escritura al cliente, escritura administrativa en juegos,
renderizado protegido del cliente y preflight CORS restringido.

## Dos servicios públicos externos — parte 3

La página `/descubrir/` presenta dos secciones y dos fuentes distintas:

| Proveedor | API pública consultada por Django | Datos mostrados |
| --- | --- | --- |
| FreeToGame | `https://www.freetogame.com/api/games` | Catálogo de juegos gratuitos, plataforma, género y enlace externo. |
| GamerPower | `https://www.gamerpower.com/api/giveaways?type=game` | Promociones de juegos completos, plataforma, vigencia, valor habitual y enlace al proveedor. |

Los dos adaptadores devuelven JSON al navegador. JavaScript utiliza `fetch()`
por separado para cargar y filtrar cada sección sin recargar la página. Si una
fuente falla, la otra conserva su propio estado. La información de GamerPower
se muestra con un [enlace activo de atribución](https://www.gamerpower.com/),
conforme a sus [términos de API](https://www.gamerpower.com/api-read).

El adaptador de GamerPower solo solicita `type=game`, valida la plataforma,
descarta registros de otros tipos o vencidos, limita a doce ofertas, limpia
el texto, conserva únicamente imágenes HTTPS y enlaces de destino HTTPS del
dominio GamerPower. Una respuesta 201 del proveedor se presenta como lista
vacía, no como error. Hay caché por plataforma de cinco minutos para reducir
solicitudes y respetar el límite publicado por la API.

El 4 de octubre de 2026 se consultaron **en vivo** ambos adaptadores con la
configuración SQLite local: FreeToGame respondió HTTP 200 con doce juegos y
GamerPower respondió HTTP 200 con doce ofertas normalizadas. Es una evidencia
puntual; la disponibilidad externa puede cambiar.

Después de esta parte, la suite completa terminó con **93 pruebas correctas**,
`manage.py check` sin problemas y `node --check` sin errores para
`servicio_ofertas.js`. Las diez pruebas nuevas abarcan renderizado de ambas
fuentes, carga asincrónica, filtros, normalización, caché, respuesta sin
ofertas, error de red, JSON malformado, enlaces inseguros y método no
permitido.

## Verificación integral — parte 4 (4 de octubre de 2026)

### Oracle local y flujos de negocio

El `ORA-01017` de la línea base se debía a que la instancia local `XEPDB1`
estaba abierta, pero no tenía el usuario/esquema `FREEGAMES`. Se creó **solo
ese esquema de desarrollo** con las credenciales y permisos indicados en el
`README.md`, y se aplicó `python manage.py migrate --noinput`. Esto modificó
la base Oracle local, no los scripts SQL ni otras bases de datos. Después,
`python manage.py check --database default` terminó sin problemas. Las
migraciones iniciales cargaron dos cuentas de prueba, cinco categorías y quince
juegos.

Se ejecutó una prueba de humo con el cliente de pruebas Django y la conexión
Oracle real. Las operaciones de escritura se hicieron en una transacción con
*rollback*, para preservar los datos iniciales:

| Flujo | Resultado observado |
| --- | --- |
| Inicio y catálogo públicos | HTTP 200 en ambas vistas. |
| Perfil sin sesión | Redirección HTTP 302 al acceso. |
| Cliente autenticado | HTTP 200 en perfil, carrito e historial; HTTP 302 al intentar administración. |
| Compra simulada temporal | Pedido creado y stock de un juego reducido de 12 a 11; tras el *rollback*, cero pedidos y stock 12. |
| Administrador autenticado | HTTP 200 en el panel administrativo. |
| Ambas API sin token | HTTP 401 en categorías y juegos. |
| Ambas API con token | HTTP 200 en categorías y juegos. |

### Navegador, validaciones y diseño adaptable

Se revisaron visualmente las páginas inicial, catálogo, registro, acceso,
recuperación, Descubrir, perfil, carrito, historial, explorador de API y
administración, según correspondía a cada rol. Se usaron las cuentas locales
de prueba `cliente` y `admin`; se cerraron sus sesiones al terminar. Para
verificar `/explorar-api/`, se generó un token temporal que se retiró de
Oracle después de la prueba.

| Ancho de pantalla | Evidencia |
| --- | --- |
| 390 px, móvil | Menú colapsable funcional; catálogo, formularios, feeds, perfil, carrito, historial, API y administración sin desbordamiento horizontal. |
| 768 px, tableta | Formulario de registro con campos de ancho completo (`col-12`) y mitades (`col-md-6`); panel de administración en dos columnas y sin desbordamiento. |
| 1440 px, escritorio | Descubrir con tres tarjetas por fila y panel administrativo con cuatro indicadores; sin desbordamiento horizontal. |

El formulario de registro vacío mostró resumen y mensajes específicos de
validación sin abandonar la página. En Descubrir, los dos feeds cargaron 12
elementos cada uno sin recarga; se comprobó que los filtros de plataforma
actualizan cada fuente de forma independiente. En `/explorar-api/`, la sesión
de cliente y su token mostraron cinco categorías y quince juegos sin recarga;
el filtro «Acción + Gratis» devolvió un único juego, Valorant. La consola del
navegador no registró errores durante la revisión.

La revisión detectó que la regla `.api-page` anulaba el *gutter* horizontal de
Bootstrap en móvil. Se reemplazó el `padding` abreviado por `padding-top` y
`padding-bottom`, manteniendo los 12 px horizontales de `.container`. Tras
recargar, el encabezado se ubicó a 12 px del borde y no hubo desbordamiento.
Las plantillas de registro, perfil, administración y explorador usan filas y
columnas Bootstrap de la cuadrícula de 12 unidades.

### Comprobaciones finales y límites

```powershell
$env:FREEGAMES_USE_SQLITE = '1'
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
Remove-Item Env:FREEGAMES_USE_SQLITE
.\.venv\Scripts\python.exe manage.py check --database default
```

Resultado: **93 pruebas correctas**, sin cambios de migración pendientes y
`manage.py check` correcto con Oracle. Los archivos JavaScript pasaron
`node --check`. `manage.py check --deploy` advirtió que la configuración de
desarrollo todavía tiene `DEBUG`, clave predeterminada y parámetros HTTPS/
cookies seguros sin activar. No se cambiaron esos valores aquí porque la
instancia local usa HTTP; deben configurarse correctamente antes de publicar
en un servidor real. La evidencia de participación equitativa en Git y la
preparación del comprimido final corresponden a la parte 5.
