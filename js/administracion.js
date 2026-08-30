(() => {
  'use strict';

  const datos = window.FreeGamesData;
  const productos = window.FreeGamesProducts;
  const compras = window.FreeGamesPurchases;

  if (!datos || !productos || !compras) {
    console.warn('No fue posible cargar el panel de administración de FreeGames.');
    return;
  }

  function escaparHTML(valor) {
    return String(valor)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function nombreRol(rol) {
    return rol === 'administrador' ? 'Administrador' : 'Cliente';
  }

  function mostrarEstado(selector, mensaje, tipo) {
    const destino = document.querySelector(selector);

    if (!destino) {
      return;
    }

    destino.textContent = mensaje;
    destino.className = `form-status ${tipo}`;
    destino.hidden = false;
    destino.focus();
  }

  function limpiarEstado(selector) {
    const destino = document.querySelector(selector);

    if (!destino) {
      return;
    }

    destino.textContent = '';
    destino.className = 'form-status';
    destino.hidden = true;
  }

  function renderizarResumen() {
    const inventario = productos.listar();
    const usuarios = datos.listarUsuarios();
    const pedidos = compras.listar();
    const disponibles = inventario.filter((producto) => producto.activo && producto.stock > 0).length;
    const agotados = inventario.filter((producto) => !producto.activo || producto.stock === 0).length;
    const clientes = usuarios.filter((usuario) => usuario.rol === 'cliente' && usuario.activo).length;
    const ventas = pedidos.reduce((total, pedido) => total + pedido.total, 0);

    document.querySelector('#admin-summary').innerHTML = `
      <article class="admin-metric"><span>Juegos disponibles</span><strong>${disponibles}</strong><small>${agotados} sin disponibilidad</small></article>
      <article class="admin-metric"><span>Clientes activos</span><strong>${clientes}</strong><small>${usuarios.length} cuentas registradas</small></article>
      <article class="admin-metric"><span>Pedidos simulados</span><strong>${pedidos.length}</strong><small>Compras confirmadas</small></article>
      <article class="admin-metric"><span>Total simulado</span><strong>${productos.formatearPrecio(ventas)}</strong><small>Sin medio de pago real</small></article>
    `;
  }

  function renderizarProductos() {
    const cuerpo = document.querySelector('#admin-products-body');

    if (!cuerpo) {
      return;
    }

    cuerpo.innerHTML = productos.listar().map((producto) => `
      <tr>
        <td><strong>${escaparHTML(producto.nombre)}</strong><small>${escaparHTML(producto.categoria)}</small></td>
        <td>${productos.formatearPrecio(producto.precio)}</td>
        <td>${producto.stock}</td>
        <td><span class="status-badge ${producto.activo && producto.stock > 0 ? 'available' : 'unavailable'}">${producto.activo && producto.stock > 0 ? 'Disponible' : 'No disponible'}</span></td>
        <td><button class="table-action" type="button" data-edit-product="${producto.id}">Editar</button></td>
      </tr>
    `).join('');
  }

  function renderizarUsuarios() {
    const cuerpo = document.querySelector('#admin-users-body');

    if (!cuerpo) {
      return;
    }

    cuerpo.innerHTML = datos.listarUsuarios().map((usuario) => `
      <tr>
        <td><strong>${escaparHTML(usuario.nombreCompleto)}</strong><small>${escaparHTML(usuario.correo)}</small></td>
        <td>${escaparHTML(usuario.nombreUsuario)}</td>
        <td>${nombreRol(usuario.rol)}</td>
        <td><span class="status-badge ${usuario.activo ? 'available' : 'unavailable'}">${usuario.activo ? 'Activa' : 'Inactiva'}</span></td>
        <td><button class="table-action" type="button" data-edit-user="${usuario.id}">Editar</button></td>
      </tr>
    `).join('');
  }

  function cargarProducto(id) {
    const producto = productos.buscar(id);

    if (!producto) {
      return;
    }

    document.querySelector('#admin-product-id').value = producto.id;
    document.querySelector('#admin-product-name').value = producto.nombre;
    document.querySelector('#admin-product-category').value = producto.categoria;
    document.querySelector('#admin-product-price').value = producto.precio;
    document.querySelector('#admin-product-stock').value = producto.stock;
    document.querySelector('#admin-product-active').value = String(producto.activo);
    limpiarEstado('#product-status');
    document.querySelector('#admin-product-name').focus();
  }

  function cargarUsuario(id) {
    const usuario = datos.buscarUsuarioPorId(id);

    if (!usuario) {
      return;
    }

    document.querySelector('#admin-user-id').value = usuario.id;
    document.querySelector('#admin-user-name').value = usuario.nombreCompleto;
    document.querySelector('#admin-user-email').value = usuario.correo;
    document.querySelector('#admin-user-role').value = usuario.rol;
    document.querySelector('#admin-user-active').value = String(usuario.activo);
    limpiarEstado('#user-status');
    document.querySelector('#admin-user-role').focus();
  }

  function valorEntero(campo) {
    return /^\d+$/.test(campo.value.trim()) ? Number.parseInt(campo.value, 10) : Number.NaN;
  }

  function conectarMantenedorProductos() {
    const formulario = document.querySelector('#admin-product-form');
    const tabla = document.querySelector('#admin-products-body');

    if (!formulario || !tabla) {
      return;
    }

    tabla.addEventListener('click', (evento) => {
      const boton = evento.target.closest('[data-edit-product]');
      if (boton) cargarProducto(boton.dataset.editProduct);
    });

    formulario.addEventListener('submit', (evento) => {
      evento.preventDefault();
      limpiarEstado('#product-status');

      const precio = valorEntero(document.querySelector('#admin-product-price'));
      const stock = valorEntero(document.querySelector('#admin-product-stock'));

      if (!Number.isInteger(precio) || precio < 0 || !Number.isInteger(stock) || stock < 0) {
        mostrarEstado('#product-status', 'Precio y disponibilidad deben ser números enteros iguales o mayores que cero.', 'error');
        return;
      }

      const producto = productos.actualizarProducto(document.querySelector('#admin-product-id').value, {
        precio,
        stock,
        activo: document.querySelector('#admin-product-active').value === 'true'
      });

      if (!producto) {
        mostrarEstado('#product-status', 'No fue posible actualizar este juego. Revisa los valores ingresados.', 'error');
        return;
      }

      renderizarResumen();
      renderizarProductos();
      mostrarEstado('#product-status', `${producto.nombre} fue actualizado correctamente.`, 'success');
    });
  }

  function conectarMantenedorUsuarios(sesion) {
    const formulario = document.querySelector('#admin-user-form');
    const tabla = document.querySelector('#admin-users-body');

    if (!formulario || !tabla) {
      return;
    }

    tabla.addEventListener('click', (evento) => {
      const boton = evento.target.closest('[data-edit-user]');
      if (boton) cargarUsuario(boton.dataset.editUser);
    });

    formulario.addEventListener('submit', (evento) => {
      evento.preventDefault();
      limpiarEstado('#user-status');

      const id = document.querySelector('#admin-user-id').value;
      const rol = document.querySelector('#admin-user-role').value;
      const activo = document.querySelector('#admin-user-active').value === 'true';

      // Evita que el único administrador de la sesión se quite permisos por accidente.
      if (id === sesion.usuario.id && (rol !== 'administrador' || !activo)) {
        mostrarEstado('#user-status', 'No puedes cambiar tu propio rol ni desactivar tu sesión desde este panel.', 'error');
        return;
      }

      const usuario = datos.actualizarUsuario(id, { rol, activo });

      if (!usuario) {
        mostrarEstado('#user-status', 'No fue posible actualizar el usuario seleccionado.', 'error');
        return;
      }

      renderizarResumen();
      renderizarUsuarios();
      mostrarEstado('#user-status', `La cuenta de ${usuario.nombreUsuario} fue actualizada correctamente.`, 'success');
    });
  }

  function iniciarAdministracion() {
    const guardia = document.querySelector('#administration-guard');
    const contenido = document.querySelector('#administration-content');

    if (!guardia || !contenido) {
      return;
    }

    const sesion = datos.obtenerSesion();

    if (!sesion || sesion.usuario.rol !== 'administrador') {
      guardia.hidden = false;
      contenido.hidden = true;
      guardia.innerHTML = `
        <h2>Acceso restringido</h2>
        <p>Esta sección está disponible únicamente para cuentas con rol administrador.</p>
        <a class="primary-link" href="login.html">Iniciar sesión</a>
      `;
      return;
    }

    guardia.hidden = true;
    contenido.hidden = false;
    renderizarResumen();
    renderizarProductos();
    renderizarUsuarios();
    cargarProducto(productos.listar()[0].id);
    cargarUsuario(datos.listarUsuarios()[0].id);
    conectarMantenedorProductos();
    conectarMantenedorUsuarios(sesion);
  }

  iniciarAdministracion();
})();
