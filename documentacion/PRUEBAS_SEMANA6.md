# Evidencias de pruebas de la semana 6

## Entorno comprobado

- Django 5.2.17.
- Oracle Database mediante el controlador `oracledb`.
- Servicio local `XEPDB1` y esquema `FREEGAMES`.
- Migraciones de `admin`, `auth`, `contenttypes`, `sessions` y `tienda` aplicadas.

## Resultado automatizado

Se ejecutaron los siguientes comandos:

```powershell
python manage.py check
$env:FREEGAMES_USE_SQLITE = "1"
python manage.py makemigrations --check --dry-run
python manage.py test tienda
Remove-Item Env:FREEGAMES_USE_SQLITE
```

Resultado: **38 pruebas aprobadas**, sin errores de configuración y sin migraciones pendientes.

## Matriz de acceso

| Funcionalidad | Visitante | Cliente | Administrador |
| --- | --- | --- | --- |
| Inicio y catálogo | Permitido | Permitido | Redirige a administración |
| Registro y login | Permitido | Redirige según rol | Redirige según rol |
| Perfil | Solicita login | Permitido | Restringido |
| Carrito y compra | Solicita login | Permitido | Restringido |
| Historial de compras | Solicita login | Solo historial propio | Restringido |
| Administración | Solicita login | Restringido | Permitido |
| CRUD de juegos | Solicita login | Restringido | Permitido mediante `POST` |
| CRUD de usuarios | Solicita login | Restringido | Permitido mediante `POST` |

## Flujos comprobados

- Registro, inicio de sesión por usuario o correo, cierre mediante `POST` y edición del perfil.
- Recuperación mediante token temporal sin revelar si el correo existe.
- Acceso directo a rutas protegidas como visitante y con un rol incorrecto.
- Rechazo de métodos HTTP no admitidos y de solicitudes `POST` sin token CSRF.
- Creación, consulta, modificación, publicación y eliminación de juegos.
- Creación, consulta, modificación y eliminación o desactivación segura de usuarios.
- Carrito de sesión, actualización de cantidades, control de stock y vaciado.
- Compra transaccional, creación de pedido y detalle, descuento de stock e historial privado.
- Protección de juegos y usuarios asociados a pedidos para conservar el historial.

## Comprobación con Oracle

La conexión real informó el motor `oracle`. Se comprobaron dos roles, dos perfiles y usuarios iniciales, cinco categorías y quince juegos. Las cuentas `cliente` y `admin` autenticaron correctamente después de ejecutar el script de datos iniciales.

También se recorrió en Oracle el registro de un cliente, la compra y su historial, el CRUD de juegos y el CRUD de usuarios. La auditoría se ejecutó dentro de una transacción con reversión: al finalizar se conservaron los conteos originales de 2 usuarios, 15 juegos y 0 pedidos, junto con el stock inicial.

El script `base_datos/02_datos_iniciales.sql` ejecutó correctamente sus operaciones `MERGE` y puede repetirse sin duplicar registros.
