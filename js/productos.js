(() => {
  'use strict';

  const almacenamiento = window.FreeGamesStore;

  if (!almacenamiento) {
    console.warn('No se cargó el almacenamiento local de FreeGames.');
    return;
  }

  const CLAVE_PRODUCTOS = 'freegames_productos';

  // El catálogo queda centralizado para que las tarjetas, el carrito y las compras usen la misma información.
  const PRODUCTOS_BASE = Object.freeze([
    { id: 'call-of-duty', nombre: 'Call of Duty', categoria: 'Acción', precio: 19990, imagen: 'img/accion.png', stock: 12, activo: true },
    { id: 'gta-v', nombre: 'Grand Theft Auto V', categoria: 'Acción', precio: 14990, imagen: 'img/gta-v.png', stock: 8, activo: true },
    { id: 'valorant', nombre: 'Valorant', categoria: 'Acción', precio: 0, imagen: 'img/valorant.png', stock: 50, activo: true },
    { id: 'pokemon', nombre: 'Pokémon', categoria: 'Aventura', precio: 24990, imagen: 'img/aventura.png', stock: 7, activo: true },
    { id: 'dungeon-quest', nombre: 'Dungeon Quest', categoria: 'Aventura', precio: 0, imagen: 'img/dungeon-quest.png', stock: 25, activo: true },
    { id: 'zelda', nombre: 'The Legend of Zelda', categoria: 'Aventura', precio: 29990, imagen: 'img/zelda.png', stock: 5, activo: true },
    { id: 'ping-pong', nombre: 'Ping Pong', categoria: 'Deportes', precio: 8990, imagen: 'img/deportes.png', stock: 14, activo: true },
    { id: 'ea-sports-fc', nombre: 'EA Sports FC', categoria: 'Deportes', precio: 27990, imagen: 'img/ea-sports-fc.png', stock: 6, activo: true },
    { id: 'rocket-league', nombre: 'Rocket League', categoria: 'Deportes', precio: 0, imagen: 'img/rocket-league.png', stock: 30, activo: true },
    { id: 'need-for-speed', nombre: 'Need for Speed', categoria: 'Carreras', precio: 17990, imagen: 'img/carreras.png', stock: 9, activo: true },
    { id: 'forza-horizon', nombre: 'Forza Horizon', categoria: 'Carreras', precio: 32990, imagen: 'img/forza-horizon.png', stock: 4, activo: true },
    { id: 'trackmania', nombre: 'Trackmania', categoria: 'Carreras', precio: 0, imagen: 'img/trackmania.png', stock: 40, activo: true },
    { id: 'damas', nombre: 'Damas (Checkers)', categoria: 'Estrategia', precio: 4990, imagen: 'img/estrategia.png', stock: 18, activo: true },
    { id: 'ajedrez-online', nombre: 'Ajedrez Online', categoria: 'Estrategia', precio: 0, imagen: 'img/ajedrez-online.png', stock: 45, activo: true },
    { id: 'age-of-empires', nombre: 'Age of Empires', categoria: 'Estrategia', precio: 19990, imagen: 'img/age-of-empires.png', stock: 7, activo: true }
  ]);

  function copiar(valor) {
    return JSON.parse(JSON.stringify(valor));
  }

  function inicializarProductos() {
    const guardados = almacenamiento.leer(CLAVE_PRODUCTOS, []);
    const productos = Array.isArray(guardados) ? guardados : [];

    PRODUCTOS_BASE.forEach((productoBase) => {
      const productoGuardado = productos.find((producto) => producto.id === productoBase.id);

      if (!productoGuardado) {
        productos.push(copiar(productoBase));
        return;
      }

      // Nombre, precio e imagen vienen del catálogo; el stock se conserva entre visitas.
      productoGuardado.nombre = productoBase.nombre;
      productoGuardado.categoria = productoBase.categoria;
      productoGuardado.precio = productoBase.precio;
      productoGuardado.imagen = productoBase.imagen;
      productoGuardado.activo = productoGuardado.activo !== false;

      if (!Number.isInteger(productoGuardado.stock) || productoGuardado.stock < 0) {
        productoGuardado.stock = productoBase.stock;
      }
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

  function actualizarStock(id, nuevoStock) {
    const productos = listar();
    const posicion = productos.findIndex((producto) => producto.id === id);

    if (posicion === -1 || !Number.isInteger(nuevoStock) || nuevoStock < 0) {
      return null;
    }

    productos[posicion].stock = nuevoStock;
    almacenamiento.guardar(CLAVE_PRODUCTOS, productos);
    return copiar(productos[posicion]);
  }

  function formatearPrecio(precio) {
    return precio === 0 ? 'Gratis' : `$${precio.toLocaleString('es-CL')}`;
  }

  function textoStock(producto) {
    if (!producto.activo || producto.stock === 0) {
      return 'Agotado';
    }

    return `Stock: ${producto.stock} ${producto.stock === 1 ? 'unidad' : 'unidades'}`;
  }

  inicializarProductos();

  window.FreeGamesProducts = Object.freeze({
    listar,
    buscar,
    actualizarStock,
    formatearPrecio,
    textoStock
  });
})();
