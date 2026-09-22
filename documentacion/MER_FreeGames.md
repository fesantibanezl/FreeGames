# Modelo entidad relación normalizado de FreeGames

El modelo separa autenticación, perfiles, roles, catálogo y pedidos. `AUTH_USER` pertenece al sistema de autenticación de Django; las otras seis tablas corresponden a la aplicación `tienda`.

```mermaid
erDiagram
    AUTH_USER ||--|| TIENDA_PERFILUSUARIO : posee
    TIENDA_ROL ||--o{ TIENDA_PERFILUSUARIO : asigna
    AUTH_USER ||--o{ TIENDA_PEDIDO : realiza
    TIENDA_CATEGORIA ||--o{ TIENDA_JUEGO : agrupa
    TIENDA_PEDIDO ||--|{ TIENDA_DETALLEPEDIDO : contiene
    TIENDA_JUEGO ||--o{ TIENDA_DETALLEPEDIDO : aparece_en

    AUTH_USER {
        int id PK
        string username UK
        string password
        string first_name
        string last_name
        string email
        boolean is_active
        boolean is_staff
    }

    TIENDA_ROL {
        bigint id PK
        string codigo UK
        string nombre
        string descripcion
    }

    TIENDA_PERFILUSUARIO {
        bigint id PK
        int usuario_id FK, UK
        bigint rol_id FK
        date fecha_nacimiento
        string direccion
        datetime creado_en
        datetime actualizado_en
    }

    TIENDA_CATEGORIA {
        bigint id PK
        string slug UK
        string nombre UK
        string icono
        string clase_css
        string resumen
        string descripcion_meta
        string imagen
        string imagen_alt
        int orden
    }

    TIENDA_JUEGO {
        bigint id PK
        bigint categoria_id FK
        string slug UK
        string nombre UK
        string descripcion
        int precio
        int stock
        boolean activo
        string imagen
        string imagen_alt
        datetime creado_en
        datetime actualizado_en
    }

    TIENDA_PEDIDO {
        bigint id PK
        int usuario_id FK
        string codigo UK
        string estado
        int total
        datetime creado_en
    }

    TIENDA_DETALLEPEDIDO {
        bigint id PK
        bigint pedido_id FK
        bigint juego_id FK
        string nombre_juego
        int precio_unitario
        int cantidad
    }
```

## Normalización

- **Primera forma normal:** cada campo guarda un valor atómico y cada tabla dispone de una clave primaria.
- **Segunda forma normal:** los atributos dependen de la clave completa. En `TIENDA_DETALLEPEDIDO`, la combinación pedido y juego es única.
- **Tercera forma normal:** roles, categorías, usuarios, juegos y pedidos se almacenan por separado. Los datos descriptivos no se repiten entre entidades relacionadas.

`NOMBRE_JUEGO` y `PRECIO_UNITARIO` se conservan en el detalle como una instantánea deliberada de la compra. Así, el historial no cambia si posteriormente se modifica el juego.
