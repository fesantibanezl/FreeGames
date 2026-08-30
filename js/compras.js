(() => {
  'use strict';

  const almacenamiento = window.FreeGamesStore;
  const productos = window.FreeGamesProducts;
  const datos = window.FreeGamesData;

  if (!almacenamiento || !productos || !datos) {
    console.warn('No fue posible cargar el módulo de compras de FreeGames.');
    return;
  }

  const CLAVE_COMPRAS = 'freegames_compras';
  const CLAVE_ULTIMA_COMPRA = 'freegames_ultima_compra';

  function listar() {
    const compras = almacenamiento.leer(CLAVE_COMPRAS, []);
    return Array.isArray(compras) ? compras : [];
  }

  function buscarPorId(id) {
    return listar().find((compra) => compra.id === id) ?? null;
  }

  function listarPorUsuario(usuarioId) {
    return listar().filter((compra) => compra.usuarioId === usuarioId);
  }

  function crearCompra(usuario, elementosCarrito) {
    if (!usuario || !Array.isArray(elementosCarrito) || elementosCarrito.length === 0) {
      return { ok: false, mensaje: 'No hay productos disponibles para registrar la compra.' };
    }

    const items = [];

    for (const elemento of elementosCarrito) {
      const producto = productos.buscar(elemento.productoId);

      if (!producto || !producto.activo) {
        return { ok: false, mensaje: 'Uno de los juegos ya no está disponible.' };
      }

      if (!Number.isInteger(elemento.cantidad) || elemento.cantidad < 1 || elemento.cantidad > producto.stock) {
        return { ok: false, mensaje: `No hay stock suficiente para ${producto.nombre}.` };
      }

      items.push({
        productoId: producto.id,
        nombre: producto.nombre,
        imagen: producto.imagen,
        precioUnitario: producto.precio,
        cantidad: elemento.cantidad,
        subtotal: producto.precio * elemento.cantidad
      });
    }

    // El stock se actualiza solo después de comprobar todos los productos del pedido.
    items.forEach((item) => {
      const producto = productos.buscar(item.productoId);
      productos.actualizarStock(producto.id, producto.stock - item.cantidad);
    });

    const fecha = new Date().toISOString();
    const compra = {
      id: `FG-${Date.now().toString().slice(-8)}-${Math.floor(Math.random() * 900 + 100)}`,
      usuarioId: usuario.id,
      nombreUsuario: usuario.nombreUsuario,
      fecha,
      estado: 'Confirmada',
      items,
      total: items.reduce((acumulado, item) => acumulado + item.subtotal, 0)
    };

    const compras = listar();
    compras.unshift(compra);
    almacenamiento.guardar(CLAVE_COMPRAS, compras);
    almacenamiento.guardar(CLAVE_ULTIMA_COMPRA, compra.id);

    return { ok: true, compra };
  }

  function obtenerUltimaCompra() {
    const id = almacenamiento.leer(CLAVE_ULTIMA_COMPRA, '');
    return typeof id === 'string' ? buscarPorId(id) : null;
  }

  function escaparHTML(valor) {
    return String(valor)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function formatearFecha(fecha) {
    return new Intl.DateTimeFormat('es-CL', {
      dateStyle: 'long',
      timeStyle: 'short'
    }).format(new Date(fecha));
  }

  function resumenItems(compra) {
    return compra.items.map((item) => `
      <li>
        <span>${escaparHTML(item.nombre)} × ${item.cantidad}</span>
        <strong>${productos.formatearPrecio(item.subtotal)}</strong>
      </li>
    `).join('');
  }

  function renderizarCompraExitosa() {
    const destino = document.querySelector('#purchase-result');

    if (!destino) {
      return;
    }

    const parametros = new URLSearchParams(window.location.search);
    const compra = buscarPorId(parametros.get('pedido')) ?? obtenerUltimaCompra();

    if (!compra) {
      destino.innerHTML = `
        <section class="access-notice">
          <h2>No encontramos una compra reciente</h2>
          <p>Agrega juegos al carrito para realizar una compra simulada.</p>
          <a class="primary-link" href="carrito.html">Ir al carrito</a>
        </section>
      `;
      return;
    }

    destino.innerHTML = `
      <section class="purchase-success" aria-labelledby="purchase-title">
        <p class="eyebrow">Compra simulada</p>
        <h1 id="purchase-title">¡Compra confirmada!</h1>
        <p>El pago fue registrado de forma simulada. No se utilizó WebPay ni se realizó un cobro real.</p>

        <div class="purchase-details">
          <div><span>Pedido</span><strong>${escaparHTML(compra.id)}</strong></div>
          <div><span>Fecha</span><strong>${formatearFecha(compra.fecha)}</strong></div>
          <div><span>Estado</span><strong class="order-status">${escaparHTML(compra.estado)}</strong></div>
        </div>

        <h2>Resumen del pedido</h2>
        <ul class="purchase-items">${resumenItems(compra)}</ul>
        <p class="purchase-total"><span>Total pagado</span><strong>${productos.formatearPrecio(compra.total)}</strong></p>

        <div class="form-actions">
          <a class="button button-primary" href="mis-compras.html">Ver mis compras</a>
          <a class="button button-secondary" href="index.html">Seguir explorando</a>
        </div>
      </section>
    `;
  }

  function renderizarHistorial() {
    const guardia = document.querySelector('#history-guard');
    const contenido = document.querySelector('#history-content');

    if (!guardia || !contenido) {
      return;
    }

    const sesion = datos.obtenerSesion();

    if (!sesion) {
      guardia.hidden = false;
      contenido.hidden = true;
      return;
    }

    if (sesion.usuario.rol !== 'cliente') {
      guardia.hidden = false;
      guardia.innerHTML = `
        <h2>Historial disponible para clientes</h2>
        <p>Las compras se asocian al rol cliente. El panel administrativo se implementará en la siguiente parte.</p>
        <a class="primary-link" href="perfil.html">Ir a mi perfil</a>
      `;
      contenido.hidden = true;
      return;
    }

    const compras = listarPorUsuario(sesion.usuario.id);
    guardia.hidden = true;
    contenido.hidden = false;

    if (compras.length === 0) {
      contenido.innerHTML = `
        <section class="empty-state">
          <h2>Aún no tienes compras</h2>
          <p>Cuando completes una compra simulada, sus detalles aparecerán aquí.</p>
          <a class="primary-link" href="index.html">Explorar juegos</a>
        </section>
      `;
      return;
    }

    contenido.innerHTML = compras.map((compra) => `
      <article class="order-card">
        <header>
          <div>
            <p class="eyebrow">Pedido ${escaparHTML(compra.id)}</p>
            <h2>${formatearFecha(compra.fecha)}</h2>
          </div>
          <span class="order-status">${escaparHTML(compra.estado)}</span>
        </header>
        <ul class="purchase-items">${resumenItems(compra)}</ul>
        <p class="purchase-total"><span>Total</span><strong>${productos.formatearPrecio(compra.total)}</strong></p>
      </article>
    `).join('');
  }

  window.FreeGamesPurchases = Object.freeze({
    crearCompra,
    buscarPorId,
    listarPorUsuario
  });

  renderizarCompraExitosa();
  renderizarHistorial();
})();
