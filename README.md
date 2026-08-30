# FreeGames

Proyecto FrontEnd para la asignatura **Programación Web — Experiencia 3**. FreeGames es un catálogo de videojuegos con registro de usuarios, roles, carrito y administración simulada, construido sin backend ni base de datos.

## Cómo ejecutar el proyecto

No requiere instalar dependencias. Abre [index.html](index.html) en un navegador moderno.

Para que el navegador trate todos los archivos como un sitio local, también se puede iniciar un servidor estático desde la carpeta del proyecto:

```powershell
python -m http.server 8000
```

Luego visita `http://localhost:8000`.

## Funcionalidades implementadas

- Catálogo con cinco categorías y quince videojuegos.
- Navegación adaptable con menú colapsable en pantallas pequeñas.
- Registro, inicio de sesión, recuperación simulada y edición de perfil.
- Validación inmediata de datos y mensajes accesibles en los formularios.
- Roles de **cliente** y **administrador** con vistas y permisos diferentes.
- Carrito con cantidades, total, disponibilidad y compra simulada sin cobro real.
- Historial de pedidos para el cliente.
- Panel administrativo para actualizar precio, disponibilidad, publicación, rol y estado de cuentas.

## Rutas principales

| Ruta | Propósito |
| --- | --- |
| `index.html` | Página inicial y acceso a categorías. |
| `registro.html` | Registro de una cuenta de cliente. |
| `login.html` | Inicio de sesión. |
| `perfil.html` | Consulta y edición del perfil activo. |
| `carrito.html` | Carrito y confirmación de una compra simulada. |
| `mis-compras.html` | Historial exclusivo del rol cliente. |
| `administracion.html` | Panel exclusivo del rol administrador. |

## Cuentas de prueba

Estas cuentas existen únicamente para revisar los roles y funcionalidades del FrontEnd. Las credenciales no se muestran dentro del formulario de inicio de sesión.

| Rol | Usuario | Contraseña |
| --- | --- | --- |
| Cliente | `cliente` | `Cliente#2026` |
| Administrador | `admin` | `Admin#2026` |

## Estructura del proyecto

```text
FreeGames/
├── css/
│   └── style.css              # Estilos, diseño adaptable y estados visuales.
├── img/                       # Ilustraciones PNG del catálogo.
├── js/
│   ├── datos-demo.js          # Usuarios, sesión y almacenamiento simulado.
│   ├── validaciones.js        # Reglas de validación de formularios.
│   ├── autenticacion.js       # Inicio de sesión, perfil y navegación por rol.
│   ├── productos.js           # Catálogo, precios y disponibilidad.
│   ├── carrito.js             # Carrito y cantidades seleccionadas.
│   ├── compras.js             # Confirmación e historial de pedidos.
│   └── administracion.js      # Mantenedores del administrador.
└── *.html                     # Páginas públicas, de cliente y administración.
```

## Consideraciones 

- Los datos se almacenan temporalmente en el navegador mediante `localStorage`; si este no está disponible, se usa memoria mientras la página permanezca abierta.
- Las contraseñas y la compra son demostrativas. En una versión real, el backend debe autenticar, proteger contraseñas, validar permisos y procesar pagos.
- WebPay u otro medio de pago no están integrados, el comprobante solo confirma una simulación.
- Las imágenes del proyecto están en formato PNG y cada imagen relevante incluye texto alternativo.
- La interfaz considera navegación por teclado, foco visible, enlace para saltar al contenido y adaptación a móvil, tableta y escritorio.

## Pruebas realizadas

- Validación de sintaxis de los archivos JavaScript.
- Registro, inicio de sesión y recuperación simulada.
- Restricción de rutas según el rol activo.
- Agregado de juegos, ajuste de cantidades, stock y compra simulada.
- Historial de compras del cliente.
- Edición administrativa de catálogo y cuentas.
- Revisión de diseño en móvil, tableta y escritorio.
