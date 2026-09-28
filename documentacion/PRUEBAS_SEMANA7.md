# Pruebas y uso de la API de la Semana 7

## Alcance evaluado

La verificación cubre los tres criterios de la actividad:

1. API REST propia con autenticación por token, permisos y filtros.
2. Consumo de un servicio REST público dentro de FreeGames sin recargar la
   página.
3. Historial incremental en Git para evidenciar el desarrollo.

Los recursos propios publicados son `Categoria` y `Juego`. La API no expone
contraseñas, perfiles, pedidos ni información personal.

## Preparación del entorno

Desde PowerShell, en la carpeta del proyecto:

```powershell
Set-Location "C:\Users\slfel\Documents\ChatGPT\FreeGames"
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

`migrate` crea las tablas necesarias para los tokens en la base configurada.
Para una revisión aislada con SQLite se puede definir temporalmente
`FREEGAMES_USE_SQLITE=1`.

## Endpoints propios

| Método | Ruta | Acceso | Resultado |
| --- | --- | --- | --- |
| `POST` | `/api/token/` | Público | Entrega un token con credenciales válidas. |
| `GET` | `/api/categorias/` | Token | Lista las categorías. |
| `POST` | `/api/categorias/` | Administrador | Crea una categoría. |
| `GET` | `/api/categorias/<id>/` | Token | Consulta una categoría. |
| `PUT`, `PATCH` | `/api/categorias/<id>/` | Administrador | Actualiza una categoría. |
| `DELETE` | `/api/categorias/<id>/` | Administrador | Elimina una categoría sin relaciones protegidas. |
| `GET` | `/api/juegos/` | Token | Lista y filtra juegos. |
| `POST` | `/api/juegos/` | Administrador | Crea un juego. |
| `GET` | `/api/juegos/<id>/` | Token | Consulta un juego. |
| `PUT`, `PATCH` | `/api/juegos/<id>/` | Administrador | Actualiza un juego. |
| `DELETE` | `/api/juegos/<id>/` | Administrador | Elimina un juego sin pedidos asociados. |

La autenticación se envía así:

```text
Authorization: Token CODIGO_DEL_TOKEN
```

## Filtros disponibles

Los filtros se aplican sobre `GET /api/juegos/` y se pueden combinar:

```text
/api/juegos/?nombre=valorant
/api/juegos/?categoria=accion
/api/juegos/?activo=true
/api/juegos/?gratis=true
/api/juegos/?categoria=accion&activo=true&gratis=false
```

`activo` y `gratis` aceptan `true`, `false`, `1`, `0`, `si`, `sí` y `no`.

## Prueba rápida con PowerShell

El siguiente ejemplo obtiene un token de administrador y consulta los juegos:

```powershell
$baseUrl = "http://127.0.0.1:8000"
$credenciales = @{
    username = "admin"
    password = "Admin#2026"
} | ConvertTo-Json

$respuestaToken = Invoke-RestMethod `
    -Method Post `
    -Uri "$baseUrl/api/token/" `
    -ContentType "application/json" `
    -Body $credenciales

$encabezados = @{
    Authorization = "Token $($respuestaToken.token)"
}

Invoke-RestMethod `
    -Method Get `
    -Uri "$baseUrl/api/juegos/?categoria=accion&activo=true" `
    -Headers $encabezados
```

Ejemplo de creación de una categoría con una cuenta administradora:

```powershell
$categoria = @{
    slug = "rol"
    nombre = "Rol"
    icono = "RPG"
    clase_css = "category-rpg"
    resumen = "Historias y evolución de personajes"
    descripcion_meta = "Juegos de rol disponibles en FreeGames."
    imagen = "tienda/img/aventura.png"
    imagen_alt = "Personajes de un videojuego de rol"
    orden = 6
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "$baseUrl/api/categorias/" `
    -Headers $encabezados `
    -ContentType "application/json" `
    -Body $categoria
```

Este segundo ejemplo modifica la base de datos y debe ejecutarse únicamente
cuando se quiera conservar o eliminar después el registro creado.

## Configuración en Postman

1. Crear un entorno con `base_url` igual a `http://127.0.0.1:8000`.
2. Enviar `POST {{base_url}}/api/token/` con cuerpo JSON:

   ```json
   {
     "username": "admin",
     "password": "Admin#2026"
   }
   ```

3. Copiar el valor `token` de la respuesta a una variable llamada `token`.
4. En las demás solicitudes agregar el encabezado:

   ```text
   Authorization: Token {{token}}
   ```

5. Probar primero las consultas y después `POST`, `PUT`, `PATCH` y `DELETE`
   con una cuenta administradora.
6. Repetir una operación de escritura con la cuenta `cliente` para comprobar
   la respuesta `403 Forbidden`.

Nunca se debe publicar un token real en GitHub, capturas o documentación.

## Consumo del servicio público

La ruta `/descubrir/` carga juegos desde FreeToGame mediante `fetch()` y
actualiza el DOM sin recargar. El navegador consulta la ruta interna
`/servicios/juegos-gratis/`; Django valida los filtros, consulta el servicio
público, normaliza los campos y mantiene el resultado cinco minutos en caché.

La interfaz permite filtrar por plataforma, género y orden. También muestra
estados de carga, éxito, ausencia de resultados, error y reintento. La fuente
queda atribuida mediante un enlace visible a FreeToGame.

## Matriz de pruebas

| Prueba | Resultado esperado | Automatizada |
| --- | --- | --- |
| Token con credenciales válidas | `200` y token persistente | Sí |
| Token con contraseña inválida | `400` sin token | Sí |
| Recurso sin token | `401 Unauthorized` | Sí |
| Recurso con token inexistente | `401 Unauthorized` | Sí |
| Lectura con cuenta cliente | `200 OK` | Sí |
| Escritura con cuenta cliente | `403 Forbidden` sin modificar datos | Sí |
| Escritura con administrador | `201 Created` | Sí |
| GET de colección | Lista JSON | Sí |
| GET de detalle existente | Objeto JSON | Sí |
| GET de detalle inexistente | `404 Not Found` | Sí |
| POST válido | Registro creado y persistente | Sí |
| POST inválido | `400 Bad Request` | Sí |
| PUT válido | Registro actualizado | Sí |
| PATCH válido | Campos indicados actualizados | Sí |
| DELETE válido | `204 No Content` | Sí |
| GET posterior a DELETE | `404 Not Found` | Sí |
| DELETE con relación protegida | `409 Conflict` | Sí |
| Filtro por nombre | Solo coincidencias parciales | Sí |
| Filtro por categoría | Solo juegos de la categoría | Sí |
| Filtros activo y gratis | Solo juegos coincidentes | Sí |
| Filtro sin coincidencias | Lista vacía con `200` | Sí |
| Booleano inválido | `400 Bad Request` | Sí |
| Página de servicio público | HTML y JavaScript disponibles | Sí |
| Carga dinámica | Uso de `fetch()` sin recarga | Sí |
| Respuesta pública válida | Datos normalizados | Sí |
| Servicio público no disponible | `502` y mensaje recuperable | Sí |
| Respuesta pública malformada | `502` sin error interno | Sí |
| Filtro externo inválido | `400` sin consultar a terceros | Sí |
| Caché externo | Una consulta para solicitudes repetidas | Sí |
| Enlace externo inseguro | Se descarta | Sí |

## Ejecución automatizada

```powershell
$env:FREEGAMES_USE_SQLITE = "1"
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test tienda api
Remove-Item Env:FREEGAMES_USE_SQLITE
python -m pip check
```

Las llamadas al servicio público se simulan en las pruebas para que la suite
sea repetible aun cuando no exista conexión a Internet. La URL real también se
debe comprobar manualmente antes de la entrega.

## Evidencia Git previa al cierre

| Parte | Commit | Evidencia |
| --- | --- | --- |
| 1 | `0a04a0c` | Infraestructura de Django REST Framework. |
| 2 | `d919f64` | Serializadores y CRUD REST. |
| 3 | `22472d2` | Token, permisos y filtros. |
| 4 | `80e8fed` | Consumo asincrónico de FreeToGame. |

Estos commits demuestran un desarrollo incremental. Para acreditar trabajo
grupal, cada integrante debe participar mediante commits propios, ramas o
revisiones visibles en el repositorio remoto; no corresponde atribuir trabajo
a colaboradores que no hayan intervenido realmente.
