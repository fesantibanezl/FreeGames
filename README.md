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

- Catálogo con cinco categorías y quince videojuegos.
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

## Consideraciones

- Django entrega las páginas y los recursos estáticos; los usuarios, la sesión, el carrito y las compras todavía se almacenan en `localStorage`.
- Los juegos creados desde el mantenedor usan la imagen representativa de la categoría seleccionada.
- Si `localStorage` no está disponible, se usa memoria mientras la página permanezca abierta.
- Las contraseñas y la compra son demostrativas. No existe un cobro real ni una integración con WebPay.
- La interfaz considera navegación por teclado, foco visible, enlace para saltar al contenido y adaptación a móvil, tableta y escritorio.

## Pruebas

Para ejecutar la revisión automatizada:

```powershell
python manage.py check
python manage.py test tienda
```

También se revisaron manualmente el registro, la recuperación, los dos roles, las restricciones de acceso, el perfil, el carrito, la compra simulada, el historial y el panel administrativo.
