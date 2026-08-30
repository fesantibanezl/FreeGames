(() => {
  'use strict';

  const almacenamiento = window.FreeGamesStore;
  const productos = window.FreeGamesProducts;
  const datos = window.FreeGamesData;
  const compras = window.FreeGamesPurchases;

  if (!almacenamiento || !productos || !datos) {
    console.warn('No fue posible cargar el módulo de carrito de FreeGames.');
    return;
  }

  const CLAVE_CARRITO = 'freegames_carrito';

  function leerCarrito() {
    const guardado = almacenamiento.leer(CLAVE_CARRITO, []);
    const elementos = Array.isArray(guardado) ? guardado : [];
    const cantidades = new Map();

    elementos.forEach((elemento) => {
      const producto = productos.buscar(elemento.productoId);
      const cantidad = Number.parseInt(elemento.cantidad, 10);

      // Si el stock cambió mientras el juego estaba en el carrito, se descarta
      // cuando ya no quedan unidades y se ajusta cuando quedan menos.
      if (producto && producto.activo && producto.stock > 0 && Number.isInteger(cantidad) && cantidad > 0) {
        cantidades.set(producto.id, Math.min((cantidades.get(producto.id) ?? 0) + cantidad, producto.stock));
      }
    });

    return [...cantidades].map(([productoId, cantidad]) => ({ productoId, cantidad }));
  }

  function guardarCarrito(elementos) {
    almacenamiento.guardar(CLAVE_CARRITO, elementos);
    actualizarContadores();
    document.dispatchEvent(new CustomEvent('freegames:cart-changed'));
  }

  function obtenerDetalle() {
    return leerCarrito().map((elemento) => {
      const producto = productos.buscar(elemento.productoId);
      return {
        ...elemento,
        producto,
        subtotal: producto.precio * elemento.cantidad
      };
    }).filter((elemento) => elemento.producto);
  }

  function cantidadTotal() {
    return leerCarrito().reduce((total, elemento) => total + elemento.cantidad, 0);
  }

  function agregar(productoId) {
    const producto = productos.buscar(productoId);

    if (!producto || !producto.activo || producto.stock === 0) {
      return { ok: false, mensaje: 'Este juego no está disponible por el momento.' };
    }

    const carrito = leerCarrito();
    const existente = carrito.find((elemento) => elemento.productoId === productoId);
    const cantidadActual = existente?.cantidad ?? 0;

    if (cantidadActual >= producto.stock) {
      return { ok: false, mensaje: `Ya alcanzaste el stock disponible de ${producto.nombre}.` };
    }

    if (existente) {
      existente.cantidad += 1;
    } else {
      carrito.push({ productoId, cantidad: 1 });
    }

    guardarCarrito(carrito);
    return { ok: true, mensaje: `${producto.nombre} fue agregado al carrito.` };
  }

  function cambiarCantidad(productoId, cantidadSolicitada) {
    const producto = productos.buscar(productoId);
    const carrito = leerCarrito();
    const elemento = carrito.find((item) => item.productoId === productoId);

    if (!producto || !elemento) {
      return { ok: false, mensaje: 'No encontramos ese juego en el carrito.' };
    }

    const cantidad = Number.parseInt(cantidadSolicitada, 10);

    if (!Number.isInteger(cantidad) || cantidad < 1) {
      return eliminar(productoId);
    }

    if (cantidad > producto.stock) {
      return { ok: false, mensaje: `Solo hay ${producto.stock} unidades disponibles de ${producto.nombre}.` };
    }

    elemento.cantidad = cantidad;
    guardarCarrito(carrito);
    return { ok: true, mensaje: 'Cantidad actualizada.' };
  }

  function eliminar(productoId) {
    const producto = productos.buscar(productoId);
    const carrito = leerCarrito().filter((elemento) => elemento.productoId !== productoId);

    guardarCarrito(carrito);
    return { ok: true, mensaje: producto ? `${producto.nombre} fue eliminado del carrito.` : 'Juego eliminado del carrito.' };
  }

  function vaciar() {
    guardarCarrito([]);
  }

  function actualizarContadores() {
    const cantidad = cantidadTotal();
    document.querySelectorAll('[data-cart-count]').forEach((contador) => {
      contador.textContent = cantidad;
      contador.hidden = cantidad === 0;
    });
  }

  function escaparHTML(valor) {
    return String(valor)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function prepararTarjetas() {
    document.querySelectorAll('[data-product-id]').forEach((tarjeta) => {
      const producto = productos.buscar(tarjeta.dataset.productId);

      if (!producto) {
        return;
      }

      const precio = tarjeta.querySelector('[data-product-price]');
      const stock = tarjeta.querySelector('[data-product-stock]');
      const boton = tarjeta.querySelector('[data-action="add-to-cart"]');

      if (precio) precio.textContent = productos.formatearPrecio(producto.precio);

      if (stock) {
        stock.textContent = productos.textoStock(producto);
        stock.classList.toggle('sold-out', producto.stock === 0 || !producto.activo);
      }

      if (!boton) {
        return;
      }

      boton.disabled = producto.stock === 0 || !producto.activo;
      boton.textContent = producto.precio === 0 ? 'Obtener gratis' : 'Agregar al carrito';

      boton.addEventListener('click', () => {
        const resultado = agregar(producto.id);
        const estado = tarjeta.querySelector('[data-product-status]');

        if (estado) {
          estado.textContent = resultado.mensaje;
          estado.className = `card-status ${resultado.ok ? 'success' : 'error'}`;
        }
      });
    });
  }

  function mostrarEstadoCarrito(mensaje, tipo) {
    const estado = document.querySelector('#cart-status');

    if (!estado) {
      return;
    }

    estado.textContent = mensaje;
    estado.className = `form-status ${tipo}`;
    estado.hidden = false;
  }

  function renderizarCarrito() {
    const lista = document.querySelector('#cart-items');
    const vacio = document.querySelector('#cart-empty');
    const resumen = document.querySelector('#cart-summary');

    if (!lista || !vacio || !resumen) {
      return;
    }

    const elementos = obtenerDetalle();

    if (elementos.length === 0) {
      lista.innerHTML = '';
      vacio.hidden = false;
      resumen.hidden = true;
      return;
    }

    vacio.hidden = true;
    resumen.hidden = false;
    lista.innerHTML = elementos.map(({ producto, cantidad, subtotal }) => `
      <article class="cart-item" data-cart-item="${producto.id}">
        <img src="${producto.imagen}" alt="${escaparHTML(producto.nombre)}">
        <div class="cart-item-info">
          <p class="eyebrow">${escaparHTML(producto.categoria)}</p>
          <h2>${escaparHTML(producto.nombre)}</h2>
          <p>${productos.formatearPrecio(producto.precio)} por unidad · ${productos.textoStock(producto)}</p>
        </div>
        <div class="cart-quantity" aria-label="Cantidad de ${escaparHTML(producto.nombre)}">
          <button type="button" data-cart-decrease="${producto.id}" aria-label="Disminuir cantidad de ${escaparHTML(producto.nombre)}">−</button>
          <input type="number" min="1" max="${producto.stock}" value="${cantidad}" data-cart-quantity="${producto.id}" aria-label="Cantidad de ${escaparHTML(producto.nombre)}">
          <button type="button" data-cart-increase="${producto.id}" aria-label="Aumentar cantidad de ${escaparHTML(producto.nombre)}" ${cantidad >= producto.stock ? 'disabled' : ''}>+</button>
        </div>
        <strong class="cart-subtotal">${productos.formatearPrecio(subtotal)}</strong>
        <button class="remove-item" type="button" data-cart-remove="${producto.id}">Eliminar</button>
      </article>
    `).join('');

    const total = elementos.reduce((acumulado, elemento) => acumulado + elemento.subtotal, 0);
    resumen.querySelector('[data-cart-total]').textContent = productos.formatearPrecio(total);
  }

  function conectarCarrito() {
    const paginaCarrito = document.querySelector('#cart-page');

    if (!paginaCarrito) {
      return;
    }

    paginaCarrito.addEventListener('click', (evento) => {
      const botonAumentar = evento.target.closest('[data-cart-increase]');
      const botonDisminuir = evento.target.closest('[data-cart-decrease]');
      const botonEliminar = evento.target.closest('[data-cart-remove]');
      const botonVaciar = evento.target.closest('[data-action="empty-cart"]');
      const botonComprar = evento.target.closest('[data-action="checkout"]');

      if (botonAumentar) {
        const id = botonAumentar.dataset.cartIncrease;
        const actual = leerCarrito().find((elemento) => elemento.productoId === id);
        const resultado = cambiarCantidad(id, (actual?.cantidad ?? 0) + 1);
        mostrarEstadoCarrito(resultado.mensaje, resultado.ok ? 'success' : 'error');
        renderizarCarrito();
      }

      if (botonDisminuir) {
        const id = botonDisminuir.dataset.cartDecrease;
        const actual = leerCarrito().find((elemento) => elemento.productoId === id);
        const resultado = cambiarCantidad(id, (actual?.cantidad ?? 1) - 1);
        mostrarEstadoCarrito(resultado.mensaje, resultado.ok ? 'success' : 'error');
        renderizarCarrito();
      }

      if (botonEliminar) {
        const resultado = eliminar(botonEliminar.dataset.cartRemove);
        mostrarEstadoCarrito(resultado.mensaje, 'success');
        renderizarCarrito();
      }

      if (botonVaciar) {
        vaciar();
        mostrarEstadoCarrito('El carrito fue vaciado.', 'success');
        renderizarCarrito();
      }

      if (botonComprar) {
        const elementos = leerCarrito();

        if (elementos.length === 0) {
          mostrarEstadoCarrito('Agrega al menos un juego antes de continuar.', 'error');
          return;
        }

        const sesion = datos.obtenerSesion();

        if (!sesion) {
          mostrarEstadoCarrito('Debes iniciar sesión como cliente para finalizar la compra.', 'error');
          return;
        }

        if (sesion.usuario.rol !== 'cliente') {
          mostrarEstadoCarrito('Las compras simuladas están disponibles para el rol cliente.', 'error');
          return;
        }

        if (!compras) {
          mostrarEstadoCarrito('No fue posible registrar la compra simulada.', 'error');
          return;
        }

        const resultado = compras.crearCompra(sesion.usuario, elementos);

        if (!resultado.ok) {
          mostrarEstadoCarrito(resultado.mensaje, 'error');
          renderizarCarrito();
          return;
        }

        vaciar();
        window.location.href = `compra-exitosa.html?pedido=${encodeURIComponent(resultado.compra.id)}`;
      }
    });

    paginaCarrito.addEventListener('change', (evento) => {
      const campoCantidad = evento.target.closest('[data-cart-quantity]');

      if (!campoCantidad) {
        return;
      }

      const resultado = cambiarCantidad(campoCantidad.dataset.cartQuantity, campoCantidad.value);
      mostrarEstadoCarrito(resultado.mensaje, resultado.ok ? 'success' : 'error');
      renderizarCarrito();
    });

    document.addEventListener('freegames:cart-changed', renderizarCarrito);
    renderizarCarrito();
  }

  actualizarContadores();
  prepararTarjetas();
  conectarCarrito();
})();
