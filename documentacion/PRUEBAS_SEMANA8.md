# Semana 8 — evidencia de la parte 2

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

No se ha validado aún Oracle en esta sesión porque las credenciales locales
generan `ORA-01017`. Tampoco se ha hecho la revisión visual en tres tamaños;
corresponde a la parte 4.
