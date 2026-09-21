# FreeGames

Proyecto para la asignatura **Programación Web — Experiencia de Aprendizaje 2**. En la semana 4, FreeGames migra su interfaz FrontEnd a Django y conserva de forma temporal los datos demostrativos en el navegador.

## Cómo ejecutar el proyecto

Se necesita Python 3.10 o una versión posterior. Desde PowerShell, ejecuta los siguientes comandos en la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Luego visita `http://127.0.0.1:8000/` en un navegador moderno. Visual Studio Code puede utilizarse para editar el proyecto, pero no es obligatorio.

## Funcionalidades implementadas

- Catálogo inicial con cinco categorías y quince videojuegos, ampliable desde el mantenedor.
- Navegación adaptable con menú colapsable en pantallas pequeñas.
- Registro, inicio de sesión, recuperación simulada y edición de perfil.
- Validación inmediata de datos y mensajes accesibles en los formularios.
- Roles de **cliente** y **administrador** con vistas y permisos diferentes.
- Carrito con cantidades, total, disponibilidad y compra simulada sin cobro real.
- Historial de pedidos para el cliente.
- Panel administrativo para registrar y modificar juegos, controlar su publicación y administrar roles y estados de cuentas.
- Vistas, plantillas y archivos estáticos organizados mediante Django.

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

## Cuentas de prueba

Estas cuentas existen únicamente para revisar los roles y funcionalidades del proyecto. Las credenciales no se muestran dentro del formulario de inicio de sesión.

| Rol | Usuario | Contraseña |
| --- | --- | --- |
| Cliente | `cliente` | `Cliente#2026` |
| Administrador | `admin` | `Admin#2026` |

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
│   ├── tests.py               # Pruebas de vistas, rutas y plantillas.
│   ├── urls.py                # Rutas de la aplicación tienda.
│   └── views.py               # Vistas que renderizan las plantillas.
├── manage.py
└── requirements.txt
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

- Django entrega las páginas y los recursos estáticos; los usuarios, la sesión, el carrito y las compras todavía se almacenan en `localStorage`.
- Los juegos creados desde el mantenedor usan la imagen representativa de la categoría seleccionada.
- Si `localStorage` no está disponible, se usa memoria mientras la página permanezca abierta.
- Las contraseñas y la compra son demostrativas. No existe un cobro real ni una integración con WebPay.
- La interfaz considera navegación por teclado, foco visible, enlace para saltar al contenido y adaptación a móvil, tableta y escritorio.
- `models.py` todavía no define persistencia propia porque los Models, las migraciones de negocio y la base de datos corresponden a la semana 5.

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
python manage.py test tienda
```

También se revisaron manualmente el registro, la recuperación, los dos roles, las restricciones de acceso, el perfil, el carrito, la compra simulada, el historial y el panel administrativo.
