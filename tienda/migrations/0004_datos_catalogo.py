from django.db import migrations


CATEGORIAS = (
    ('accion', 'Acción', '⚡', 'category-action', 'Combate y adrenalina', 'Juegos de acción disponibles en FreeGames.', 'tienda/img/accion.png', 'Soldado futurista en una ciudad iluminada'),
    ('aventura', 'Aventura', '🧭', 'category-adventure', 'Descubre nuevos mundos', 'Juegos de aventura disponibles en FreeGames.', 'tienda/img/aventura.png', 'Explorador con una criatura fantástica en un valle'),
    ('deportes', 'Deportes', '🏓', 'category-sports', 'Compite y supera tus marcas', 'Juegos de deportes disponibles en FreeGames.', 'tienda/img/deportes.png', 'Partido de tenis de mesa en una arena moderna'),
    ('carreras', 'Carreras', '🏁', 'category-racing', 'Velocidad sin límites', 'Juegos de carreras disponibles en FreeGames.', 'tienda/img/carreras.png', 'Automóvil deportivo corriendo por una ciudad nocturna'),
    ('estrategia', 'Estrategia', '♟', 'category-strategy', 'Piensa cada movimiento', 'Juegos de estrategia disponibles en FreeGames.', 'tienda/img/estrategia.png', 'Fichas de damas sobre un tablero oscuro'),
)


JUEGOS = (
    ('accion', 'call-of-duty', 'Call of Duty', 'Entra en intensas misiones tácticas donde la rapidez, la precisión y el trabajo en equipo deciden cada combate.', 19990, 12, 'tienda/img/accion.png', 'Arte original de un soldado futurista en acción'),
    ('accion', 'gta-v', 'Grand Theft Auto V', 'Explora una ciudad abierta, completa misiones y conduce vehículos en una aventura urbana llena de posibilidades.', 14990, 8, 'tienda/img/gta-v.png', 'Conductor junto a un automóvil deportivo en una ciudad nocturna'),
    ('accion', 'valorant', 'Valorant', 'Combina precisión táctica y habilidades especiales en partidas competitivas por equipos.', 0, 50, 'tienda/img/valorant.png', 'Agentes futuristas usando habilidades de energía en una arena'),
    ('aventura', 'pokemon', 'Pokémon', 'Recorre regiones llenas de sorpresas, conoce criaturas extraordinarias y vive una aventura donde cada encuentro cuenta.', 24990, 7, 'tienda/img/aventura.png', 'Arte original de un explorador y una criatura fantástica'),
    ('aventura', 'dungeon-quest', 'Dungeon Quest', 'Explora mazmorras, encuentra tesoros y mejora a tu héroe mientras descubres secretos bajo tierra.', 0, 25, 'tienda/img/dungeon-quest.png', 'Aventurero y criatura mágica entrando en una mazmorra antigua'),
    ('aventura', 'zelda', 'The Legend of Zelda', 'Recorre un reino abierto, resuelve antiguos acertijos y enfréntate a desafíos en una travesía legendaria.', 29990, 5, 'tienda/img/zelda.png', 'Explorador élfico observando un reino fantástico con islas flotantes'),
    ('deportes', 'ping-pong', 'Ping Pong', 'Domina el saque, responde con efecto y reta a tus rivales en partidos rápidos de tenis de mesa.', 8990, 14, 'tienda/img/deportes.png', 'Arte original de un partido de tenis de mesa'),
    ('deportes', 'ea-sports-fc', 'EA Sports FC', 'Forma tu equipo, compite en grandes estadios y disfruta partidos de fútbol con ritmo profesional.', 27990, 6, 'tienda/img/ea-sports-fc.png', 'Dos futbolistas disputando el balón en un estadio iluminado'),
    ('deportes', 'rocket-league', 'Rocket League', 'Combina fútbol y vehículos acrobáticos en encuentros rápidos donde cada salto puede cambiar el marcador.', 0, 30, 'tienda/img/rocket-league.png', 'Automóviles impulsados por cohetes disputando un balón futurista'),
    ('carreras', 'need-for-speed', 'Need for Speed', 'Acelera por calles iluminadas, mejora tu vehículo y demuestra quién domina las carreras urbanas.', 17990, 9, 'tienda/img/carreras.png', 'Arte original de un automóvil deportivo en una carrera nocturna'),
    ('carreras', 'forza-horizon', 'Forza Horizon', 'Conduce por paisajes abiertos, participa en festivales y colecciona vehículos de alto rendimiento.', 32990, 4, 'tienda/img/forza-horizon.png', 'Automóvil deportivo recorriendo una carretera de montaña al atardecer'),
    ('carreras', 'trackmania', 'Trackmania', 'Supera circuitos imposibles, mejora tus tiempos y compite contra jugadores de todo el mundo.', 0, 40, 'tienda/img/trackmania.png', 'Automóvil de carreras en una pista elevada con curvas y giros extremos'),
    ('estrategia', 'damas', 'Damas (Checkers)', 'Anticipa a tu rival, protege tus fichas y conquista el tablero en este clásico desafío de estrategia.', 4990, 18, 'tienda/img/estrategia.png', 'Arte original de fichas de damas sobre un tablero'),
    ('estrategia', 'ajedrez-online', 'Ajedrez Online', 'Planea cada movimiento, practica aperturas y desafía a rivales en partidas de distintos ritmos.', 0, 45, 'tienda/img/ajedrez-online.png', 'Piezas de ajedrez negras y marfil sobre un tablero iluminado'),
    ('estrategia', 'age-of-empires', 'Age of Empires', 'Construye tu civilización, administra recursos y dirige ejércitos en batallas históricas de estrategia en tiempo real.', 19990, 7, 'tienda/img/age-of-empires.png', 'Civilización medieval con castillo, recursos y ejército preparado para la batalla'),
)


def crear_catalogo(apps, schema_editor):
    Categoria = apps.get_model('tienda', 'Categoria')
    Juego = apps.get_model('tienda', 'Juego')
    base_datos = schema_editor.connection.alias
    categorias = {}

    for orden, datos in enumerate(CATEGORIAS, start=1):
        slug, nombre, icono, clase_css, resumen, meta, imagen, alt = datos
        categoria, _ = Categoria.objects.using(base_datos).update_or_create(
            slug=slug,
            defaults={
                'nombre': nombre,
                'icono': icono,
                'clase_css': clase_css,
                'resumen': resumen,
                'descripcion_meta': meta,
                'imagen': imagen,
                'imagen_alt': alt,
                'orden': orden,
            },
        )
        categorias[slug] = categoria

    for datos in JUEGOS:
        categoria_slug, slug, nombre, descripcion, precio, stock, imagen, alt = datos
        Juego.objects.using(base_datos).update_or_create(
            slug=slug,
            defaults={
                'categoria': categorias[categoria_slug],
                'nombre': nombre,
                'descripcion': descripcion,
                'precio': precio,
                'stock': stock,
                'activo': True,
                'imagen': imagen,
                'imagen_alt': alt,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ('tienda', '0003_categoria_juego_pedido_detallepedido'),
    ]

    operations = [
        migrations.RunPython(
            crear_catalogo,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
