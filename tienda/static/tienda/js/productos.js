(() => {
  'use strict';

  const almacenamiento = window.FreeGamesStore;

  if (!almacenamiento) {
    console.warn('No se cargó el almacenamiento local de FreeGames.');
    return;
  }

  const CLAVE_PRODUCTOS = 'freegames_productos';
  const rutaEstatica = window.FreeGamesConfig?.staticBase ?? '/static/tienda/';
  const CATEGORIAS = Object.freeze({
    accion: Object.freeze({ slug: 'accion', nombre: 'Acción', imagen: `${rutaEstatica}img/accion.png` }),
    aventura: Object.freeze({ slug: 'aventura', nombre: 'Aventura', imagen: `${rutaEstatica}img/aventura.png` }),
    deportes: Object.freeze({ slug: 'deportes', nombre: 'Deportes', imagen: `${rutaEstatica}img/deportes.png` }),
    carreras: Object.freeze({ slug: 'carreras', nombre: 'Carreras', imagen: `${rutaEstatica}img/carreras.png` }),
    estrategia: Object.freeze({ slug: 'estrategia', nombre: 'Estrategia', imagen: `${rutaEstatica}img/estrategia.png` })
  });

  // La descripción y la categoría permiten reconstruir el catálogo con los cambios del mantenedor.
  const PRODUCTOS_BASE = Object.freeze([
    { id: 'call-of-duty', nombre: 'Call of Duty', categoriaSlug: 'accion', precio: 19990, imagen: `${rutaEstatica}img/accion.png`, stock: 12, activo: true, descripcion: 'Entra en intensas misiones tácticas donde la rapidez, la precisión y el trabajo en equipo deciden cada combate.' },
    { id: 'gta-v', nombre: 'Grand Theft Auto V', categoriaSlug: 'accion', precio: 14990, imagen: `${rutaEstatica}img/gta-v.png`, stock: 8, activo: true, descripcion: 'Explora una ciudad abierta, completa misiones y conduce vehículos en una aventura urbana llena de posibilidades.' },
    { id: 'valorant', nombre: 'Valorant', categoriaSlug: 'accion', precio: 0, imagen: `${rutaEstatica}img/valorant.png`, stock: 50, activo: true, descripcion: 'Combina precisión táctica y habilidades especiales en partidas competitivas por equipos.' },
    { id: 'pokemon', nombre: 'Pokémon', categoriaSlug: 'aventura', precio: 24990, imagen: `${rutaEstatica}img/aventura.png`, stock: 7, activo: true, descripcion: 'Recorre regiones llenas de sorpresas, conoce criaturas extraordinarias y vive una aventura donde cada encuentro cuenta.' },
    { id: 'dungeon-quest', nombre: 'Dungeon Quest', categoriaSlug: 'aventura', precio: 0, imagen: `${rutaEstatica}img/dungeon-quest.png`, stock: 25, activo: true, descripcion: 'Explora mazmorras, encuentra tesoros y mejora a tu héroe mientras descubres secretos bajo tierra.' },
    { id: 'zelda', nombre: 'The Legend of Zelda', categoriaSlug: 'aventura', precio: 29990, imagen: `${rutaEstatica}img/zelda.png`, stock: 5, activo: true, descripcion: 'Recorre un reino abierto, resuelve antiguos acertijos y enfréntate a desafíos en una travesía legendaria.' },
    { id: 'ping-pong', nombre: 'Ping Pong', categoriaSlug: 'deportes', precio: 8990, imagen: `${rutaEstatica}img/deportes.png`, stock: 14, activo: true, descripcion: 'Domina el saque, responde con efecto y reta a tus rivales en partidos rápidos de tenis de mesa.' },
    { id: 'ea-sports-fc', nombre: 'EA Sports FC', categoriaSlug: 'deportes', precio: 27990, imagen: `${rutaEstatica}img/ea-sports-fc.png`, stock: 6, activo: true, descripcion: 'Forma tu equipo, compite en grandes estadios y disfruta partidos de fútbol con ritmo profesional.' },
    { id: 'rocket-league', nombre: 'Rocket League', categoriaSlug: 'deportes', precio: 0, imagen: `${rutaEstatica}img/rocket-league.png`, stock: 30, activo: true, descripcion: 'Combina fútbol y vehículos acrobáticos en encuentros rápidos donde cada salto puede cambiar el marcador.' },
    { id: 'need-for-speed', nombre: 'Need for Speed', categoriaSlug: 'carreras', precio: 17990, imagen: `${rutaEstatica}img/carreras.png`, stock: 9, activo: true, descripcion: 'Acelera por calles iluminadas, mejora tu vehículo y demuestra quién domina las carreras urbanas.' },
    { id: 'forza-horizon', nombre: 'Forza Horizon', categoriaSlug: 'carreras', precio: 32990, imagen: `${rutaEstatica}img/forza-horizon.png`, stock: 4, activo: true, descripcion: 'Conduce por paisajes abiertos, participa en festivales y colecciona vehículos de alto rendimiento.' },
    { id: 'trackmania', nombre: 'Trackmania', categoriaSlug: 'carreras', precio: 0, imagen: `${rutaEstatica}img/trackmania.png`, stock: 40, activo: true, descripcion: 'Supera circuitos imposibles, mejora tus tiempos y compite contra jugadores de todo el mundo.' },
    { id: 'damas', nombre: 'Damas (Checkers)', categoriaSlug: 'estrategia', precio: 4990, imagen: `${rutaEstatica}img/estrategia.png`, stock: 18, activo: true, descripcion: 'Anticipa a tu rival, protege tus fichas y conquista el tablero en este clásico desafío de estrategia.' },
    { id: 'ajedrez-online', nombre: 'Ajedrez Online', categoriaSlug: 'estrategia', precio: 0, imagen: `${rutaEstatica}img/ajedrez-online.png`, stock: 45, activo: true, descripcion: 'Planea cada movimiento, practica aperturas y desafía a rivales en partidas de distintos ritmos.' },
    { id: 'age-of-empires', nombre: 'Age of Empires', categoriaSlug: 'estrategia', precio: 19990, imagen: `${rutaEstatica}img/age-of-empires.png`, stock: 7, activo: true, descripcion: 'Construye tu civilización, administra recursos y dirige ejércitos en batallas históricas de estrategia en tiempo real.' }
  ]);

  function copiar(valor) {
    return JSON.parse(JSON.stringify(valor));
  }

  function normalizar(valor) {
    return String(valor ?? '').trim().toLocaleLowerCase('es');
  }

  function obtenerCategoria(slug) {
    return CATEGORIAS[String(slug ?? '').trim().toLocaleLowerCase('es')] ?? null;
  }

  function inferirCategoriaSlug(nombre) {
    const valor = normalizar(nombre);
    return Object.values(CATEGORIAS).find((categoria) => normalizar(categoria.nombre) === valor)?.slug ?? '';
  }

  function enteroNoNegativo(valor) {
    const numero = Number(valor);
    return Number.isInteger(numero) && numero >= 0 ? numero : null;
  }

  function normalizarProductoGuardado(producto, productoBase = null) {
    const categoriaSlug = obtenerCategoria(producto?.categoriaSlug)?.slug
      || inferirCategoriaSlug(producto?.categoria)
      || productoBase?.categoriaSlug;
    const categoria = obtenerCategoria(categoriaSlug);
    const nombre = String(producto?.nombre ?? productoBase?.nombre ?? '').trim();
    const descripcion = String(producto?.descripcion ?? productoBase?.descripcion ?? '').trim();
    const precio = enteroNoNegativo(producto?.precio ?? productoBase?.precio);
    const stock = enteroNoNegativo(producto?.stock ?? productoBase?.stock);

    if (!producto?.id || !categoria || nombre.length < 2 || !descripcion || precio === null || stock === null) {
      return null;
    }

    const usaImagenCategoria = producto?.usaImagenCategoria === true || (!productoBase && !producto?.imagen);
    const imagen = usaImagenCategoria
      ? categoria.imagen
      : String(producto?.imagen ?? productoBase?.imagen ?? categoria.imagen);

    return {
      id: String(producto.id),
      nombre,
      categoriaSlug: categoria.slug,
      categoria: categoria.nombre,
      descripcion,
      precio,
      imagen,
      imagenAlt: String(producto?.imagenAlt ?? `Portada de ${nombre}`),
      stock,
      activo: producto?.activo !== false,
      personalizado: producto?.personalizado === true || !productoBase,
      usaImagenCategoria
    };
  }

  function inicializarProductos() {
    const guardados = almacenamiento.leer(CLAVE_PRODUCTOS, []);
    const productosGuardados = Array.isArray(guardados) ? guardados : [];
    const productos = [];

    PRODUCTOS_BASE.forEach((productoBase) => {
      const productoGuardado = productosGuardados.find((producto) => producto.id === productoBase.id);
      const normalizado = normalizarProductoGuardado(
        productoGuardado ?? { ...productoBase, personalizado: false, usaImagenCategoria: false },
        productoBase
      );

      if (normalizado) productos.push(normalizado);
    });

    productosGuardados
      .filter((producto) => !PRODUCTOS_BASE.some((productoBase) => productoBase.id === producto.id))
      .forEach((producto) => {
        const normalizado = normalizarProductoGuardado(producto);
        if (normalizado) productos.push(normalizado);
      });

    almacenamiento.guardar(CLAVE_PRODUCTOS, productos);
    return productos;
  }

  function listar() {
    return almacenamiento.leer(CLAVE_PRODUCTOS, PRODUCTOS_BASE);
  }

  function buscar(id) {
    return listar().find((producto) => producto.id === id) ?? null;
  }

  function existeNombre(nombre, idExcluido = '') {
    const valorBuscado = normalizar(nombre);
    return listar().some((producto) => producto.id !== idExcluido && normalizar(producto.nombre) === valorBuscado);
  }

  function generarId(nombre) {
    const base = normalizar(nombre)
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '') || 'juego';
    let id = `juego-${base}`;
    let correlativo = 2;

    while (buscar(id)) {
      id = `juego-${base}-${correlativo}`;
      correlativo += 1;
    }

    return id;
  }

  function validarDatosProducto(datos, idExcluido = '') {
    const nombre = String(datos?.nombre ?? '').trim();
    const descripcion = String(datos?.descripcion ?? '').trim();
    const categoria = obtenerCategoria(datos?.categoriaSlug);
    const precio = enteroNoNegativo(datos?.precio);
    const stock = enteroNoNegativo(datos?.stock);

    if (
      nombre.length < 2
      || nombre.length > 60
      || descripcion.length < 10
      || descripcion.length > 220
      || !categoria
      || precio === null
      || stock === null
      || typeof datos?.activo !== 'boolean'
      || existeNombre(nombre, idExcluido)
    ) {
      return null;
    }

    return { nombre, descripcion, categoria, precio, stock, activo: datos.activo };
  }

  function crearProducto(datos) {
    const valores = validarDatosProducto(datos);

    if (!valores) {
      return null;
    }

    const productos = listar();
    const producto = {
      id: generarId(valores.nombre),
      nombre: valores.nombre,
      categoriaSlug: valores.categoria.slug,
      categoria: valores.categoria.nombre,
      descripcion: valores.descripcion,
      precio: valores.precio,
      imagen: valores.categoria.imagen,
      imagenAlt: `Imagen representativa de ${valores.nombre}`,
      stock: valores.stock,
      activo: valores.activo,
      personalizado: true,
      usaImagenCategoria: true
    };

    productos.push(producto);
    almacenamiento.guardar(CLAVE_PRODUCTOS, productos);
    return copiar(producto);
  }

  function actualizarStock(id, nuevoStock) {
    const productos = listar();
    const posicion = productos.findIndex((producto) => producto.id === id);
    const stock = enteroNoNegativo(nuevoStock);

    if (posicion === -1 || stock === null) {
      return null;
    }

    productos[posicion].stock = stock;
    almacenamiento.guardar(CLAVE_PRODUCTOS, productos);
    return copiar(productos[posicion]);
  }

  function actualizarProducto(id, cambios) {
    const productos = listar();
    const posicion = productos.findIndex((producto) => producto.id === id);
    const valores = validarDatosProducto(cambios, id);

    if (posicion === -1 || !valores) {
      return null;
    }

    const productoAnterior = productos[posicion];
    productos[posicion] = {
      ...productoAnterior,
      nombre: valores.nombre,
      categoriaSlug: valores.categoria.slug,
      categoria: valores.categoria.nombre,
      descripcion: valores.descripcion,
      precio: valores.precio,
      stock: valores.stock,
      activo: valores.activo,
      imagen: productoAnterior.usaImagenCategoria ? valores.categoria.imagen : productoAnterior.imagen,
      imagenAlt: `Portada de ${valores.nombre}`
    };

    almacenamiento.guardar(CLAVE_PRODUCTOS, productos);
    return copiar(productos[posicion]);
  }

  function cambiarEstadoProducto(id, activo) {
    const productos = listar();
    const posicion = productos.findIndex((producto) => producto.id === id);

    if (posicion === -1 || typeof activo !== 'boolean') {
      return null;
    }

    productos[posicion].activo = activo;
    almacenamiento.guardar(CLAVE_PRODUCTOS, productos);
    return copiar(productos[posicion]);
  }

  function listarCategorias() {
    return copiar(Object.values(CATEGORIAS));
  }

  function formatearPrecio(precio) {
    return precio === 0 ? 'Gratis' : `$${precio.toLocaleString('es-CL')}`;
  }

  function textoStock(producto) {
    if (!producto.activo) {
      return 'Oculto del catálogo';
    }

    if (producto.stock === 0) {
      return 'Agotado';
    }

    return `Stock: ${producto.stock} ${producto.stock === 1 ? 'unidad' : 'unidades'}`;
  }

  inicializarProductos();

  window.FreeGamesProducts = Object.freeze({
    listar,
    buscar,
    existeNombre,
    crearProducto,
    actualizarStock,
    actualizarProducto,
    cambiarEstadoProducto,
    listarCategorias,
    formatearPrecio,
    textoStock
  });
})();
