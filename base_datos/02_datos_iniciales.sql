-- FreeGames - datos iniciales para Oracle
-- Equivale a las migraciones de datos 0002 y 0004.
-- Los MERGE permiten ejecutar el script nuevamente sin duplicar registros.

SET DEFINE OFF;

MERGE INTO TIENDA_ROL destino
USING (SELECT N'cliente' CODIGO, N'Cliente' NOMBRE, N'Consulta el catálogo y administra su propio perfil.' DESCRIPCION FROM DUAL) fuente
ON (destino.CODIGO = fuente.CODIGO)
WHEN MATCHED THEN UPDATE SET
    destino.NOMBRE = fuente.NOMBRE, destino.DESCRIPCION = fuente.DESCRIPCION
WHEN NOT MATCHED THEN INSERT (CODIGO, NOMBRE, DESCRIPCION)
    VALUES (fuente.CODIGO, fuente.NOMBRE, fuente.DESCRIPCION);

MERGE INTO TIENDA_ROL destino
USING (SELECT N'administrador' CODIGO, N'Administrador' NOMBRE, N'Accede al panel destinado a la administración de recursos.' DESCRIPCION FROM DUAL) fuente
ON (destino.CODIGO = fuente.CODIGO)
WHEN MATCHED THEN UPDATE SET
    destino.NOMBRE = fuente.NOMBRE, destino.DESCRIPCION = fuente.DESCRIPCION
WHEN NOT MATCHED THEN INSERT (CODIGO, NOMBRE, DESCRIPCION)
    VALUES (fuente.CODIGO, fuente.NOMBRE, fuente.DESCRIPCION);

MERGE INTO AUTH_USER destino
USING (SELECT
    N'cliente' USERNAME, N'pbkdf2_sha256$1000000$W295FmxaFUstPzVGaoDiZl$voVsCeXk1LR0vDr/nORIm7ohcgZ9HhhYWManaUWnaAo=' PASSWORD,
    N'Cliente' FIRST_NAME, N'FreeGames' LAST_NAME, N'cliente@freegames.cl' EMAIL,
    0 IS_STAFF, 0 IS_SUPERUSER, 1 IS_ACTIVE
    FROM DUAL) fuente
ON (destino.USERNAME = fuente.USERNAME)
WHEN MATCHED THEN UPDATE SET
    destino.PASSWORD = fuente.PASSWORD, destino.FIRST_NAME = fuente.FIRST_NAME,
    destino.LAST_NAME = fuente.LAST_NAME, destino.EMAIL = fuente.EMAIL,
    destino.IS_STAFF = fuente.IS_STAFF, destino.IS_SUPERUSER = fuente.IS_SUPERUSER,
    destino.IS_ACTIVE = fuente.IS_ACTIVE
WHEN NOT MATCHED THEN INSERT
    (PASSWORD, LAST_LOGIN, IS_SUPERUSER, USERNAME, FIRST_NAME, LAST_NAME,
     EMAIL, IS_STAFF, IS_ACTIVE, DATE_JOINED)
    VALUES
    (fuente.PASSWORD, NULL, fuente.IS_SUPERUSER, fuente.USERNAME,
     fuente.FIRST_NAME, fuente.LAST_NAME, fuente.EMAIL, fuente.IS_STAFF,
     fuente.IS_ACTIVE, SYSTIMESTAMP);

MERGE INTO AUTH_USER destino
USING (SELECT
    N'admin' USERNAME, N'pbkdf2_sha256$1000000$tJT0TFgIXLYFR1or9ZykqU$qqNYR/jyezccFUgrevxn7Xp+9vpxSrDZ/VqhCL2WJfs=' PASSWORD,
    N'Administrador' FIRST_NAME, N'FreeGames' LAST_NAME, N'admin@freegames.cl' EMAIL,
    1 IS_STAFF, 1 IS_SUPERUSER, 1 IS_ACTIVE
    FROM DUAL) fuente
ON (destino.USERNAME = fuente.USERNAME)
WHEN MATCHED THEN UPDATE SET
    destino.PASSWORD = fuente.PASSWORD, destino.FIRST_NAME = fuente.FIRST_NAME,
    destino.LAST_NAME = fuente.LAST_NAME, destino.EMAIL = fuente.EMAIL,
    destino.IS_STAFF = fuente.IS_STAFF, destino.IS_SUPERUSER = fuente.IS_SUPERUSER,
    destino.IS_ACTIVE = fuente.IS_ACTIVE
WHEN NOT MATCHED THEN INSERT
    (PASSWORD, LAST_LOGIN, IS_SUPERUSER, USERNAME, FIRST_NAME, LAST_NAME,
     EMAIL, IS_STAFF, IS_ACTIVE, DATE_JOINED)
    VALUES
    (fuente.PASSWORD, NULL, fuente.IS_SUPERUSER, fuente.USERNAME,
     fuente.FIRST_NAME, fuente.LAST_NAME, fuente.EMAIL, fuente.IS_STAFF,
     fuente.IS_ACTIVE, SYSTIMESTAMP);

MERGE INTO TIENDA_PERFILUSUARIO destino
USING (SELECT usuario.ID USUARIO_ID, rol.ID ROL_ID
       FROM AUTH_USER usuario JOIN TIENDA_ROL rol ON rol.CODIGO = N'cliente'
       WHERE usuario.USERNAME = N'cliente') fuente
ON (destino.USUARIO_ID = fuente.USUARIO_ID)
WHEN MATCHED THEN UPDATE SET
    destino.ROL_ID = fuente.ROL_ID, destino.FECHA_NACIMIENTO = DATE '2000-01-01',
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (FECHA_NACIMIENTO, DIRECCION, CREADO_EN, ACTUALIZADO_EN, USUARIO_ID, ROL_ID)
    VALUES (DATE '2000-01-01', NULL, SYSTIMESTAMP, SYSTIMESTAMP, fuente.USUARIO_ID, fuente.ROL_ID);

MERGE INTO TIENDA_PERFILUSUARIO destino
USING (SELECT usuario.ID USUARIO_ID, rol.ID ROL_ID
       FROM AUTH_USER usuario JOIN TIENDA_ROL rol ON rol.CODIGO = N'administrador'
       WHERE usuario.USERNAME = N'admin') fuente
ON (destino.USUARIO_ID = fuente.USUARIO_ID)
WHEN MATCHED THEN UPDATE SET
    destino.ROL_ID = fuente.ROL_ID, destino.FECHA_NACIMIENTO = DATE '1990-01-01',
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (FECHA_NACIMIENTO, DIRECCION, CREADO_EN, ACTUALIZADO_EN, USUARIO_ID, ROL_ID)
    VALUES (DATE '1990-01-01', NULL, SYSTIMESTAMP, SYSTIMESTAMP, fuente.USUARIO_ID, fuente.ROL_ID);

MERGE INTO TIENDA_CATEGORIA destino
USING (SELECT
    N'accion' SLUG, N'Acción' NOMBRE, N'⚡' ICONO,
    N'category-action' CLASE_CSS, N'Combate y adrenalina' RESUMEN,
    N'Juegos de acción disponibles en FreeGames.' DESCRIPCION_META, N'tienda/img/accion.png' IMAGEN,
    N'Soldado futurista en una ciudad iluminada' IMAGEN_ALT, 1 ORDEN
    FROM DUAL) fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.NOMBRE = fuente.NOMBRE, destino.ICONO = fuente.ICONO,
    destino.CLASE_CSS = fuente.CLASE_CSS, destino.RESUMEN = fuente.RESUMEN,
    destino.DESCRIPCION_META = fuente.DESCRIPCION_META, destino.IMAGEN = fuente.IMAGEN,
    destino.IMAGEN_ALT = fuente.IMAGEN_ALT, destino.ORDEN = fuente.ORDEN
WHEN NOT MATCHED THEN INSERT
    (SLUG, NOMBRE, ICONO, CLASE_CSS, RESUMEN, DESCRIPCION_META, IMAGEN, IMAGEN_ALT, ORDEN)
    VALUES
    (fuente.SLUG, fuente.NOMBRE, fuente.ICONO, fuente.CLASE_CSS, fuente.RESUMEN,
     fuente.DESCRIPCION_META, fuente.IMAGEN, fuente.IMAGEN_ALT, fuente.ORDEN);

MERGE INTO TIENDA_CATEGORIA destino
USING (SELECT
    N'aventura' SLUG, N'Aventura' NOMBRE, N'🧭' ICONO,
    N'category-adventure' CLASE_CSS, N'Descubre nuevos mundos' RESUMEN,
    N'Juegos de aventura disponibles en FreeGames.' DESCRIPCION_META, N'tienda/img/aventura.png' IMAGEN,
    N'Explorador con una criatura fantástica en un valle' IMAGEN_ALT, 2 ORDEN
    FROM DUAL) fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.NOMBRE = fuente.NOMBRE, destino.ICONO = fuente.ICONO,
    destino.CLASE_CSS = fuente.CLASE_CSS, destino.RESUMEN = fuente.RESUMEN,
    destino.DESCRIPCION_META = fuente.DESCRIPCION_META, destino.IMAGEN = fuente.IMAGEN,
    destino.IMAGEN_ALT = fuente.IMAGEN_ALT, destino.ORDEN = fuente.ORDEN
WHEN NOT MATCHED THEN INSERT
    (SLUG, NOMBRE, ICONO, CLASE_CSS, RESUMEN, DESCRIPCION_META, IMAGEN, IMAGEN_ALT, ORDEN)
    VALUES
    (fuente.SLUG, fuente.NOMBRE, fuente.ICONO, fuente.CLASE_CSS, fuente.RESUMEN,
     fuente.DESCRIPCION_META, fuente.IMAGEN, fuente.IMAGEN_ALT, fuente.ORDEN);

MERGE INTO TIENDA_CATEGORIA destino
USING (SELECT
    N'deportes' SLUG, N'Deportes' NOMBRE, N'🏓' ICONO,
    N'category-sports' CLASE_CSS, N'Compite y supera tus marcas' RESUMEN,
    N'Juegos de deportes disponibles en FreeGames.' DESCRIPCION_META, N'tienda/img/deportes.png' IMAGEN,
    N'Partido de tenis de mesa en una arena moderna' IMAGEN_ALT, 3 ORDEN
    FROM DUAL) fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.NOMBRE = fuente.NOMBRE, destino.ICONO = fuente.ICONO,
    destino.CLASE_CSS = fuente.CLASE_CSS, destino.RESUMEN = fuente.RESUMEN,
    destino.DESCRIPCION_META = fuente.DESCRIPCION_META, destino.IMAGEN = fuente.IMAGEN,
    destino.IMAGEN_ALT = fuente.IMAGEN_ALT, destino.ORDEN = fuente.ORDEN
WHEN NOT MATCHED THEN INSERT
    (SLUG, NOMBRE, ICONO, CLASE_CSS, RESUMEN, DESCRIPCION_META, IMAGEN, IMAGEN_ALT, ORDEN)
    VALUES
    (fuente.SLUG, fuente.NOMBRE, fuente.ICONO, fuente.CLASE_CSS, fuente.RESUMEN,
     fuente.DESCRIPCION_META, fuente.IMAGEN, fuente.IMAGEN_ALT, fuente.ORDEN);

MERGE INTO TIENDA_CATEGORIA destino
USING (SELECT
    N'carreras' SLUG, N'Carreras' NOMBRE, N'🏁' ICONO,
    N'category-racing' CLASE_CSS, N'Velocidad sin límites' RESUMEN,
    N'Juegos de carreras disponibles en FreeGames.' DESCRIPCION_META, N'tienda/img/carreras.png' IMAGEN,
    N'Automóvil deportivo corriendo por una ciudad nocturna' IMAGEN_ALT, 4 ORDEN
    FROM DUAL) fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.NOMBRE = fuente.NOMBRE, destino.ICONO = fuente.ICONO,
    destino.CLASE_CSS = fuente.CLASE_CSS, destino.RESUMEN = fuente.RESUMEN,
    destino.DESCRIPCION_META = fuente.DESCRIPCION_META, destino.IMAGEN = fuente.IMAGEN,
    destino.IMAGEN_ALT = fuente.IMAGEN_ALT, destino.ORDEN = fuente.ORDEN
WHEN NOT MATCHED THEN INSERT
    (SLUG, NOMBRE, ICONO, CLASE_CSS, RESUMEN, DESCRIPCION_META, IMAGEN, IMAGEN_ALT, ORDEN)
    VALUES
    (fuente.SLUG, fuente.NOMBRE, fuente.ICONO, fuente.CLASE_CSS, fuente.RESUMEN,
     fuente.DESCRIPCION_META, fuente.IMAGEN, fuente.IMAGEN_ALT, fuente.ORDEN);

MERGE INTO TIENDA_CATEGORIA destino
USING (SELECT
    N'estrategia' SLUG, N'Estrategia' NOMBRE, N'♟' ICONO,
    N'category-strategy' CLASE_CSS, N'Piensa cada movimiento' RESUMEN,
    N'Juegos de estrategia disponibles en FreeGames.' DESCRIPCION_META, N'tienda/img/estrategia.png' IMAGEN,
    N'Fichas de damas sobre un tablero oscuro' IMAGEN_ALT, 5 ORDEN
    FROM DUAL) fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.NOMBRE = fuente.NOMBRE, destino.ICONO = fuente.ICONO,
    destino.CLASE_CSS = fuente.CLASE_CSS, destino.RESUMEN = fuente.RESUMEN,
    destino.DESCRIPCION_META = fuente.DESCRIPCION_META, destino.IMAGEN = fuente.IMAGEN,
    destino.IMAGEN_ALT = fuente.IMAGEN_ALT, destino.ORDEN = fuente.ORDEN
WHEN NOT MATCHED THEN INSERT
    (SLUG, NOMBRE, ICONO, CLASE_CSS, RESUMEN, DESCRIPCION_META, IMAGEN, IMAGEN_ALT, ORDEN)
    VALUES
    (fuente.SLUG, fuente.NOMBRE, fuente.ICONO, fuente.CLASE_CSS, fuente.RESUMEN,
     fuente.DESCRIPCION_META, fuente.IMAGEN, fuente.IMAGEN_ALT, fuente.ORDEN);

MERGE INTO TIENDA_JUEGO destino
USING (SELECT categoria.ID CATEGORIA_ID,
    N'call-of-duty' SLUG, N'Call of Duty' NOMBRE, N'Entra en intensas misiones tácticas donde la rapidez, la precisión y el trabajo en equipo deciden cada combate.' DESCRIPCION,
    19990 PRECIO, 12 STOCK, 1 ACTIVO, N'tienda/img/accion.png' IMAGEN, N'Arte original de un soldado futurista en acción' IMAGEN_ALT
    FROM TIENDA_CATEGORIA categoria WHERE categoria.SLUG = N'accion') fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.CATEGORIA_ID = fuente.CATEGORIA_ID, destino.NOMBRE = fuente.NOMBRE,
    destino.DESCRIPCION = fuente.DESCRIPCION, destino.PRECIO = fuente.PRECIO,
    destino.STOCK = fuente.STOCK, destino.ACTIVO = fuente.ACTIVO,
    destino.IMAGEN = fuente.IMAGEN, destino.IMAGEN_ALT = fuente.IMAGEN_ALT,
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (CATEGORIA_ID, SLUG, NOMBRE, DESCRIPCION, PRECIO, STOCK, ACTIVO,
     IMAGEN, IMAGEN_ALT, CREADO_EN, ACTUALIZADO_EN)
    VALUES
    (fuente.CATEGORIA_ID, fuente.SLUG, fuente.NOMBRE, fuente.DESCRIPCION,
     fuente.PRECIO, fuente.STOCK, fuente.ACTIVO, fuente.IMAGEN, fuente.IMAGEN_ALT,
     SYSTIMESTAMP, SYSTIMESTAMP);

MERGE INTO TIENDA_JUEGO destino
USING (SELECT categoria.ID CATEGORIA_ID,
    N'gta-v' SLUG, N'Grand Theft Auto V' NOMBRE, N'Explora una ciudad abierta, completa misiones y conduce vehículos en una aventura urbana llena de posibilidades.' DESCRIPCION,
    14990 PRECIO, 8 STOCK, 1 ACTIVO, N'tienda/img/gta-v.png' IMAGEN, N'Conductor junto a un automóvil deportivo en una ciudad nocturna' IMAGEN_ALT
    FROM TIENDA_CATEGORIA categoria WHERE categoria.SLUG = N'accion') fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.CATEGORIA_ID = fuente.CATEGORIA_ID, destino.NOMBRE = fuente.NOMBRE,
    destino.DESCRIPCION = fuente.DESCRIPCION, destino.PRECIO = fuente.PRECIO,
    destino.STOCK = fuente.STOCK, destino.ACTIVO = fuente.ACTIVO,
    destino.IMAGEN = fuente.IMAGEN, destino.IMAGEN_ALT = fuente.IMAGEN_ALT,
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (CATEGORIA_ID, SLUG, NOMBRE, DESCRIPCION, PRECIO, STOCK, ACTIVO,
     IMAGEN, IMAGEN_ALT, CREADO_EN, ACTUALIZADO_EN)
    VALUES
    (fuente.CATEGORIA_ID, fuente.SLUG, fuente.NOMBRE, fuente.DESCRIPCION,
     fuente.PRECIO, fuente.STOCK, fuente.ACTIVO, fuente.IMAGEN, fuente.IMAGEN_ALT,
     SYSTIMESTAMP, SYSTIMESTAMP);

MERGE INTO TIENDA_JUEGO destino
USING (SELECT categoria.ID CATEGORIA_ID,
    N'valorant' SLUG, N'Valorant' NOMBRE, N'Combina precisión táctica y habilidades especiales en partidas competitivas por equipos.' DESCRIPCION,
    0 PRECIO, 50 STOCK, 1 ACTIVO, N'tienda/img/valorant.png' IMAGEN, N'Agentes futuristas usando habilidades de energía en una arena' IMAGEN_ALT
    FROM TIENDA_CATEGORIA categoria WHERE categoria.SLUG = N'accion') fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.CATEGORIA_ID = fuente.CATEGORIA_ID, destino.NOMBRE = fuente.NOMBRE,
    destino.DESCRIPCION = fuente.DESCRIPCION, destino.PRECIO = fuente.PRECIO,
    destino.STOCK = fuente.STOCK, destino.ACTIVO = fuente.ACTIVO,
    destino.IMAGEN = fuente.IMAGEN, destino.IMAGEN_ALT = fuente.IMAGEN_ALT,
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (CATEGORIA_ID, SLUG, NOMBRE, DESCRIPCION, PRECIO, STOCK, ACTIVO,
     IMAGEN, IMAGEN_ALT, CREADO_EN, ACTUALIZADO_EN)
    VALUES
    (fuente.CATEGORIA_ID, fuente.SLUG, fuente.NOMBRE, fuente.DESCRIPCION,
     fuente.PRECIO, fuente.STOCK, fuente.ACTIVO, fuente.IMAGEN, fuente.IMAGEN_ALT,
     SYSTIMESTAMP, SYSTIMESTAMP);

MERGE INTO TIENDA_JUEGO destino
USING (SELECT categoria.ID CATEGORIA_ID,
    N'pokemon' SLUG, N'Pokémon' NOMBRE, N'Recorre regiones llenas de sorpresas, conoce criaturas extraordinarias y vive una aventura donde cada encuentro cuenta.' DESCRIPCION,
    24990 PRECIO, 7 STOCK, 1 ACTIVO, N'tienda/img/aventura.png' IMAGEN, N'Arte original de un explorador y una criatura fantástica' IMAGEN_ALT
    FROM TIENDA_CATEGORIA categoria WHERE categoria.SLUG = N'aventura') fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.CATEGORIA_ID = fuente.CATEGORIA_ID, destino.NOMBRE = fuente.NOMBRE,
    destino.DESCRIPCION = fuente.DESCRIPCION, destino.PRECIO = fuente.PRECIO,
    destino.STOCK = fuente.STOCK, destino.ACTIVO = fuente.ACTIVO,
    destino.IMAGEN = fuente.IMAGEN, destino.IMAGEN_ALT = fuente.IMAGEN_ALT,
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (CATEGORIA_ID, SLUG, NOMBRE, DESCRIPCION, PRECIO, STOCK, ACTIVO,
     IMAGEN, IMAGEN_ALT, CREADO_EN, ACTUALIZADO_EN)
    VALUES
    (fuente.CATEGORIA_ID, fuente.SLUG, fuente.NOMBRE, fuente.DESCRIPCION,
     fuente.PRECIO, fuente.STOCK, fuente.ACTIVO, fuente.IMAGEN, fuente.IMAGEN_ALT,
     SYSTIMESTAMP, SYSTIMESTAMP);

MERGE INTO TIENDA_JUEGO destino
USING (SELECT categoria.ID CATEGORIA_ID,
    N'dungeon-quest' SLUG, N'Dungeon Quest' NOMBRE, N'Explora mazmorras, encuentra tesoros y mejora a tu héroe mientras descubres secretos bajo tierra.' DESCRIPCION,
    0 PRECIO, 25 STOCK, 1 ACTIVO, N'tienda/img/dungeon-quest.png' IMAGEN, N'Aventurero y criatura mágica entrando en una mazmorra antigua' IMAGEN_ALT
    FROM TIENDA_CATEGORIA categoria WHERE categoria.SLUG = N'aventura') fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.CATEGORIA_ID = fuente.CATEGORIA_ID, destino.NOMBRE = fuente.NOMBRE,
    destino.DESCRIPCION = fuente.DESCRIPCION, destino.PRECIO = fuente.PRECIO,
    destino.STOCK = fuente.STOCK, destino.ACTIVO = fuente.ACTIVO,
    destino.IMAGEN = fuente.IMAGEN, destino.IMAGEN_ALT = fuente.IMAGEN_ALT,
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (CATEGORIA_ID, SLUG, NOMBRE, DESCRIPCION, PRECIO, STOCK, ACTIVO,
     IMAGEN, IMAGEN_ALT, CREADO_EN, ACTUALIZADO_EN)
    VALUES
    (fuente.CATEGORIA_ID, fuente.SLUG, fuente.NOMBRE, fuente.DESCRIPCION,
     fuente.PRECIO, fuente.STOCK, fuente.ACTIVO, fuente.IMAGEN, fuente.IMAGEN_ALT,
     SYSTIMESTAMP, SYSTIMESTAMP);

MERGE INTO TIENDA_JUEGO destino
USING (SELECT categoria.ID CATEGORIA_ID,
    N'zelda' SLUG, N'The Legend of Zelda' NOMBRE, N'Recorre un reino abierto, resuelve antiguos acertijos y enfréntate a desafíos en una travesía legendaria.' DESCRIPCION,
    29990 PRECIO, 5 STOCK, 1 ACTIVO, N'tienda/img/zelda.png' IMAGEN, N'Explorador élfico observando un reino fantástico con islas flotantes' IMAGEN_ALT
    FROM TIENDA_CATEGORIA categoria WHERE categoria.SLUG = N'aventura') fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.CATEGORIA_ID = fuente.CATEGORIA_ID, destino.NOMBRE = fuente.NOMBRE,
    destino.DESCRIPCION = fuente.DESCRIPCION, destino.PRECIO = fuente.PRECIO,
    destino.STOCK = fuente.STOCK, destino.ACTIVO = fuente.ACTIVO,
    destino.IMAGEN = fuente.IMAGEN, destino.IMAGEN_ALT = fuente.IMAGEN_ALT,
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (CATEGORIA_ID, SLUG, NOMBRE, DESCRIPCION, PRECIO, STOCK, ACTIVO,
     IMAGEN, IMAGEN_ALT, CREADO_EN, ACTUALIZADO_EN)
    VALUES
    (fuente.CATEGORIA_ID, fuente.SLUG, fuente.NOMBRE, fuente.DESCRIPCION,
     fuente.PRECIO, fuente.STOCK, fuente.ACTIVO, fuente.IMAGEN, fuente.IMAGEN_ALT,
     SYSTIMESTAMP, SYSTIMESTAMP);

MERGE INTO TIENDA_JUEGO destino
USING (SELECT categoria.ID CATEGORIA_ID,
    N'ping-pong' SLUG, N'Ping Pong' NOMBRE, N'Domina el saque, responde con efecto y reta a tus rivales en partidos rápidos de tenis de mesa.' DESCRIPCION,
    8990 PRECIO, 14 STOCK, 1 ACTIVO, N'tienda/img/deportes.png' IMAGEN, N'Arte original de un partido de tenis de mesa' IMAGEN_ALT
    FROM TIENDA_CATEGORIA categoria WHERE categoria.SLUG = N'deportes') fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.CATEGORIA_ID = fuente.CATEGORIA_ID, destino.NOMBRE = fuente.NOMBRE,
    destino.DESCRIPCION = fuente.DESCRIPCION, destino.PRECIO = fuente.PRECIO,
    destino.STOCK = fuente.STOCK, destino.ACTIVO = fuente.ACTIVO,
    destino.IMAGEN = fuente.IMAGEN, destino.IMAGEN_ALT = fuente.IMAGEN_ALT,
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (CATEGORIA_ID, SLUG, NOMBRE, DESCRIPCION, PRECIO, STOCK, ACTIVO,
     IMAGEN, IMAGEN_ALT, CREADO_EN, ACTUALIZADO_EN)
    VALUES
    (fuente.CATEGORIA_ID, fuente.SLUG, fuente.NOMBRE, fuente.DESCRIPCION,
     fuente.PRECIO, fuente.STOCK, fuente.ACTIVO, fuente.IMAGEN, fuente.IMAGEN_ALT,
     SYSTIMESTAMP, SYSTIMESTAMP);

MERGE INTO TIENDA_JUEGO destino
USING (SELECT categoria.ID CATEGORIA_ID,
    N'ea-sports-fc' SLUG, N'EA Sports FC' NOMBRE, N'Forma tu equipo, compite en grandes estadios y disfruta partidos de fútbol con ritmo profesional.' DESCRIPCION,
    27990 PRECIO, 6 STOCK, 1 ACTIVO, N'tienda/img/ea-sports-fc.png' IMAGEN, N'Dos futbolistas disputando el balón en un estadio iluminado' IMAGEN_ALT
    FROM TIENDA_CATEGORIA categoria WHERE categoria.SLUG = N'deportes') fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.CATEGORIA_ID = fuente.CATEGORIA_ID, destino.NOMBRE = fuente.NOMBRE,
    destino.DESCRIPCION = fuente.DESCRIPCION, destino.PRECIO = fuente.PRECIO,
    destino.STOCK = fuente.STOCK, destino.ACTIVO = fuente.ACTIVO,
    destino.IMAGEN = fuente.IMAGEN, destino.IMAGEN_ALT = fuente.IMAGEN_ALT,
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (CATEGORIA_ID, SLUG, NOMBRE, DESCRIPCION, PRECIO, STOCK, ACTIVO,
     IMAGEN, IMAGEN_ALT, CREADO_EN, ACTUALIZADO_EN)
    VALUES
    (fuente.CATEGORIA_ID, fuente.SLUG, fuente.NOMBRE, fuente.DESCRIPCION,
     fuente.PRECIO, fuente.STOCK, fuente.ACTIVO, fuente.IMAGEN, fuente.IMAGEN_ALT,
     SYSTIMESTAMP, SYSTIMESTAMP);

MERGE INTO TIENDA_JUEGO destino
USING (SELECT categoria.ID CATEGORIA_ID,
    N'rocket-league' SLUG, N'Rocket League' NOMBRE, N'Combina fútbol y vehículos acrobáticos en encuentros rápidos donde cada salto puede cambiar el marcador.' DESCRIPCION,
    0 PRECIO, 30 STOCK, 1 ACTIVO, N'tienda/img/rocket-league.png' IMAGEN, N'Automóviles impulsados por cohetes disputando un balón futurista' IMAGEN_ALT
    FROM TIENDA_CATEGORIA categoria WHERE categoria.SLUG = N'deportes') fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.CATEGORIA_ID = fuente.CATEGORIA_ID, destino.NOMBRE = fuente.NOMBRE,
    destino.DESCRIPCION = fuente.DESCRIPCION, destino.PRECIO = fuente.PRECIO,
    destino.STOCK = fuente.STOCK, destino.ACTIVO = fuente.ACTIVO,
    destino.IMAGEN = fuente.IMAGEN, destino.IMAGEN_ALT = fuente.IMAGEN_ALT,
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (CATEGORIA_ID, SLUG, NOMBRE, DESCRIPCION, PRECIO, STOCK, ACTIVO,
     IMAGEN, IMAGEN_ALT, CREADO_EN, ACTUALIZADO_EN)
    VALUES
    (fuente.CATEGORIA_ID, fuente.SLUG, fuente.NOMBRE, fuente.DESCRIPCION,
     fuente.PRECIO, fuente.STOCK, fuente.ACTIVO, fuente.IMAGEN, fuente.IMAGEN_ALT,
     SYSTIMESTAMP, SYSTIMESTAMP);

MERGE INTO TIENDA_JUEGO destino
USING (SELECT categoria.ID CATEGORIA_ID,
    N'need-for-speed' SLUG, N'Need for Speed' NOMBRE, N'Acelera por calles iluminadas, mejora tu vehículo y demuestra quién domina las carreras urbanas.' DESCRIPCION,
    17990 PRECIO, 9 STOCK, 1 ACTIVO, N'tienda/img/carreras.png' IMAGEN, N'Arte original de un automóvil deportivo en una carrera nocturna' IMAGEN_ALT
    FROM TIENDA_CATEGORIA categoria WHERE categoria.SLUG = N'carreras') fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.CATEGORIA_ID = fuente.CATEGORIA_ID, destino.NOMBRE = fuente.NOMBRE,
    destino.DESCRIPCION = fuente.DESCRIPCION, destino.PRECIO = fuente.PRECIO,
    destino.STOCK = fuente.STOCK, destino.ACTIVO = fuente.ACTIVO,
    destino.IMAGEN = fuente.IMAGEN, destino.IMAGEN_ALT = fuente.IMAGEN_ALT,
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (CATEGORIA_ID, SLUG, NOMBRE, DESCRIPCION, PRECIO, STOCK, ACTIVO,
     IMAGEN, IMAGEN_ALT, CREADO_EN, ACTUALIZADO_EN)
    VALUES
    (fuente.CATEGORIA_ID, fuente.SLUG, fuente.NOMBRE, fuente.DESCRIPCION,
     fuente.PRECIO, fuente.STOCK, fuente.ACTIVO, fuente.IMAGEN, fuente.IMAGEN_ALT,
     SYSTIMESTAMP, SYSTIMESTAMP);

MERGE INTO TIENDA_JUEGO destino
USING (SELECT categoria.ID CATEGORIA_ID,
    N'forza-horizon' SLUG, N'Forza Horizon' NOMBRE, N'Conduce por paisajes abiertos, participa en festivales y colecciona vehículos de alto rendimiento.' DESCRIPCION,
    32990 PRECIO, 4 STOCK, 1 ACTIVO, N'tienda/img/forza-horizon.png' IMAGEN, N'Automóvil deportivo recorriendo una carretera de montaña al atardecer' IMAGEN_ALT
    FROM TIENDA_CATEGORIA categoria WHERE categoria.SLUG = N'carreras') fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.CATEGORIA_ID = fuente.CATEGORIA_ID, destino.NOMBRE = fuente.NOMBRE,
    destino.DESCRIPCION = fuente.DESCRIPCION, destino.PRECIO = fuente.PRECIO,
    destino.STOCK = fuente.STOCK, destino.ACTIVO = fuente.ACTIVO,
    destino.IMAGEN = fuente.IMAGEN, destino.IMAGEN_ALT = fuente.IMAGEN_ALT,
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (CATEGORIA_ID, SLUG, NOMBRE, DESCRIPCION, PRECIO, STOCK, ACTIVO,
     IMAGEN, IMAGEN_ALT, CREADO_EN, ACTUALIZADO_EN)
    VALUES
    (fuente.CATEGORIA_ID, fuente.SLUG, fuente.NOMBRE, fuente.DESCRIPCION,
     fuente.PRECIO, fuente.STOCK, fuente.ACTIVO, fuente.IMAGEN, fuente.IMAGEN_ALT,
     SYSTIMESTAMP, SYSTIMESTAMP);

MERGE INTO TIENDA_JUEGO destino
USING (SELECT categoria.ID CATEGORIA_ID,
    N'trackmania' SLUG, N'Trackmania' NOMBRE, N'Supera circuitos imposibles, mejora tus tiempos y compite contra jugadores de todo el mundo.' DESCRIPCION,
    0 PRECIO, 40 STOCK, 1 ACTIVO, N'tienda/img/trackmania.png' IMAGEN, N'Automóvil de carreras en una pista elevada con curvas y giros extremos' IMAGEN_ALT
    FROM TIENDA_CATEGORIA categoria WHERE categoria.SLUG = N'carreras') fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.CATEGORIA_ID = fuente.CATEGORIA_ID, destino.NOMBRE = fuente.NOMBRE,
    destino.DESCRIPCION = fuente.DESCRIPCION, destino.PRECIO = fuente.PRECIO,
    destino.STOCK = fuente.STOCK, destino.ACTIVO = fuente.ACTIVO,
    destino.IMAGEN = fuente.IMAGEN, destino.IMAGEN_ALT = fuente.IMAGEN_ALT,
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (CATEGORIA_ID, SLUG, NOMBRE, DESCRIPCION, PRECIO, STOCK, ACTIVO,
     IMAGEN, IMAGEN_ALT, CREADO_EN, ACTUALIZADO_EN)
    VALUES
    (fuente.CATEGORIA_ID, fuente.SLUG, fuente.NOMBRE, fuente.DESCRIPCION,
     fuente.PRECIO, fuente.STOCK, fuente.ACTIVO, fuente.IMAGEN, fuente.IMAGEN_ALT,
     SYSTIMESTAMP, SYSTIMESTAMP);

MERGE INTO TIENDA_JUEGO destino
USING (SELECT categoria.ID CATEGORIA_ID,
    N'damas' SLUG, N'Damas (Checkers)' NOMBRE, N'Anticipa a tu rival, protege tus fichas y conquista el tablero en este clásico desafío de estrategia.' DESCRIPCION,
    4990 PRECIO, 18 STOCK, 1 ACTIVO, N'tienda/img/estrategia.png' IMAGEN, N'Arte original de fichas de damas sobre un tablero' IMAGEN_ALT
    FROM TIENDA_CATEGORIA categoria WHERE categoria.SLUG = N'estrategia') fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.CATEGORIA_ID = fuente.CATEGORIA_ID, destino.NOMBRE = fuente.NOMBRE,
    destino.DESCRIPCION = fuente.DESCRIPCION, destino.PRECIO = fuente.PRECIO,
    destino.STOCK = fuente.STOCK, destino.ACTIVO = fuente.ACTIVO,
    destino.IMAGEN = fuente.IMAGEN, destino.IMAGEN_ALT = fuente.IMAGEN_ALT,
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (CATEGORIA_ID, SLUG, NOMBRE, DESCRIPCION, PRECIO, STOCK, ACTIVO,
     IMAGEN, IMAGEN_ALT, CREADO_EN, ACTUALIZADO_EN)
    VALUES
    (fuente.CATEGORIA_ID, fuente.SLUG, fuente.NOMBRE, fuente.DESCRIPCION,
     fuente.PRECIO, fuente.STOCK, fuente.ACTIVO, fuente.IMAGEN, fuente.IMAGEN_ALT,
     SYSTIMESTAMP, SYSTIMESTAMP);

MERGE INTO TIENDA_JUEGO destino
USING (SELECT categoria.ID CATEGORIA_ID,
    N'ajedrez-online' SLUG, N'Ajedrez Online' NOMBRE, N'Planea cada movimiento, practica aperturas y desafía a rivales en partidas de distintos ritmos.' DESCRIPCION,
    0 PRECIO, 45 STOCK, 1 ACTIVO, N'tienda/img/ajedrez-online.png' IMAGEN, N'Piezas de ajedrez negras y marfil sobre un tablero iluminado' IMAGEN_ALT
    FROM TIENDA_CATEGORIA categoria WHERE categoria.SLUG = N'estrategia') fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.CATEGORIA_ID = fuente.CATEGORIA_ID, destino.NOMBRE = fuente.NOMBRE,
    destino.DESCRIPCION = fuente.DESCRIPCION, destino.PRECIO = fuente.PRECIO,
    destino.STOCK = fuente.STOCK, destino.ACTIVO = fuente.ACTIVO,
    destino.IMAGEN = fuente.IMAGEN, destino.IMAGEN_ALT = fuente.IMAGEN_ALT,
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (CATEGORIA_ID, SLUG, NOMBRE, DESCRIPCION, PRECIO, STOCK, ACTIVO,
     IMAGEN, IMAGEN_ALT, CREADO_EN, ACTUALIZADO_EN)
    VALUES
    (fuente.CATEGORIA_ID, fuente.SLUG, fuente.NOMBRE, fuente.DESCRIPCION,
     fuente.PRECIO, fuente.STOCK, fuente.ACTIVO, fuente.IMAGEN, fuente.IMAGEN_ALT,
     SYSTIMESTAMP, SYSTIMESTAMP);

MERGE INTO TIENDA_JUEGO destino
USING (SELECT categoria.ID CATEGORIA_ID,
    N'age-of-empires' SLUG, N'Age of Empires' NOMBRE, N'Construye tu civilización, administra recursos y dirige ejércitos en batallas históricas de estrategia en tiempo real.' DESCRIPCION,
    19990 PRECIO, 7 STOCK, 1 ACTIVO, N'tienda/img/age-of-empires.png' IMAGEN, N'Civilización medieval con castillo, recursos y ejército preparado para la batalla' IMAGEN_ALT
    FROM TIENDA_CATEGORIA categoria WHERE categoria.SLUG = N'estrategia') fuente
ON (destino.SLUG = fuente.SLUG)
WHEN MATCHED THEN UPDATE SET
    destino.CATEGORIA_ID = fuente.CATEGORIA_ID, destino.NOMBRE = fuente.NOMBRE,
    destino.DESCRIPCION = fuente.DESCRIPCION, destino.PRECIO = fuente.PRECIO,
    destino.STOCK = fuente.STOCK, destino.ACTIVO = fuente.ACTIVO,
    destino.IMAGEN = fuente.IMAGEN, destino.IMAGEN_ALT = fuente.IMAGEN_ALT,
    destino.ACTUALIZADO_EN = SYSTIMESTAMP
WHEN NOT MATCHED THEN INSERT
    (CATEGORIA_ID, SLUG, NOMBRE, DESCRIPCION, PRECIO, STOCK, ACTIVO,
     IMAGEN, IMAGEN_ALT, CREADO_EN, ACTUALIZADO_EN)
    VALUES
    (fuente.CATEGORIA_ID, fuente.SLUG, fuente.NOMBRE, fuente.DESCRIPCION,
     fuente.PRECIO, fuente.STOCK, fuente.ACTIVO, fuente.IMAGEN, fuente.IMAGEN_ALT,
     SYSTIMESTAMP, SYSTIMESTAMP);

COMMIT;

-- Verificacion esperada: 2 roles, 2 perfiles, 5 categorias y 15 juegos.
SELECT 'ROLES' ELEMENTO, COUNT(*) TOTAL FROM TIENDA_ROL
UNION ALL SELECT 'PERFILES', COUNT(*) FROM TIENDA_PERFILUSUARIO
UNION ALL SELECT 'CATEGORIAS', COUNT(*) FROM TIENDA_CATEGORIA
UNION ALL SELECT 'JUEGOS', COUNT(*) FROM TIENDA_JUEGO;
