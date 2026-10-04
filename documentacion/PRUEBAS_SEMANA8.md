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

Resultado del 4 de octubre de 2026: `manage.py check` sin problemas, **83
pruebas correctas** y JavaScript sin errores de sintaxis. Las pruebas nuevas
incluyen acceso sin token e inválido a ambas API, uso real de un token obtenido
en `/api/token/`, verificación de que la sesión web no sustituye al token,
denegación de escritura al cliente, escritura administrativa en juegos,
renderizado protegido del cliente y preflight CORS restringido.

No se ha validado aún la base Oracle de esta sesión porque sus credenciales
locales generan `ORA-01017`. Tampoco se ha hecho la revisión visual en tres
tamaños ni la integración del segundo servicio externo; corresponden a las
partes 3 y 4.
