(() => {
  'use strict';

  const datos = window.FreeGamesData;
  const productos = window.FreeGamesProducts;
  const compras = window.FreeGamesPurchases;
  const rutas = window.FreeGamesConfig?.routes ?? {};

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
    const noDisponibles = inventario.filter((producto) => !producto.activo || producto.stock === 0).length;
    const clientes = usuarios.filter((usuario) => usuario.rol === 'cliente' && usuario.activo).length;
    const ventas = pedidos.reduce((total, pedido) => total + pedido.total, 0);

    document.querySelector('#admin-summary').innerHTML = `
      <article class="admin-metric"><span>Juegos disponibles</span><strong>${disponibles}</strong><small>${noDisponibles} sin disponibilidad</small></article>
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

    cuerpo.innerHTML = productos.listar().map((producto) => {
      const publicado = producto.activo && producto.stock > 0;
      const estado = producto.activo ? (producto.stock > 0 ? 'Publicado' : 'Sin stock') : 'Oculto';
      const accionEstado = producto.activo ? 'Quitar' : 'Publicar';
      const claseEstado = producto.activo ? 'danger' : 'restore';

      return `
        <tr>
          <td data-label="Juego"><strong>${escaparHTML(producto.nombre)}</strong><small>${escaparHTML(producto.categoria)}</small></td>
          <td data-label="Precio">${productos.formatearPrecio(producto.precio)}</td>
          <td data-label="Disponibilidad">${producto.stock}</td>
          <td data-label="Estado"><span class="status-badge ${publicado ? 'available' : 'unavailable'}">${estado}</span></td>
          <td data-label="Acciones">
            <div class="table-actions">
              <button class="table-action" type="button" data-edit-product="${escaparHTML(producto.id)}">Editar</button>
              <button class="table-action ${claseEstado}" type="button" data-toggle-product="${escaparHTML(producto.id)}" data-next-active="${!producto.activo}">${accionEstado}</button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  }

  function renderizarUsuarios() {
    const cuerpo = document.querySelector('#admin-users-body');

    if (!cuerpo) {
      return;
    }

    cuerpo.innerHTML = datos.listarUsuarios().map((usuario) => `
      <tr>
        <td data-label="Nombre y correo"><strong>${escaparHTML(usuario.nombreCompleto)}</strong><small>${escaparHTML(usuario.correo)}</small></td>
        <td data-label="Usuario">${escaparHTML(usuario.nombreUsuario)}</td>
        <td data-label="Rol">${nombreRol(usuario.rol)}</td>
        <td data-label="Estado"><span class="status-badge ${usuario.activo ? 'available' : 'unavailable'}">${usuario.activo ? 'Activa' : 'Inactiva'}</span></td>
        <td data-label="Acciones"><button class="table-action" type="button" data-edit-user="${escaparHTML(usuario.id)}">Editar</button></td>
      </tr>
    `).join('');
  }

  function obtenerCamposProducto() {
    return {
      id: document.querySelector('#admin-product-id'),
      nombre: document.querySelector('#admin-product-name'),
      categoria: document.querySelector('#admin-product-category'),
      descripcion: document.querySelector('#admin-product-description'),
      precio: document.querySelector('#admin-product-price'),
      stock: document.querySelector('#admin-product-stock'),
      activo: document.querySelector('#admin-product-active')
    };
  }

  function prepararNuevoProducto(enfocar = true) {
    const formulario = document.querySelector('#admin-product-form');
    const campos = obtenerCamposProducto();

    formulario.reset();
    campos.id.value = '';
    campos.categoria.value = 'accion';
    campos.precio.value = '0';
    campos.stock.value = '0';
    campos.activo.value = 'true';
    document.querySelector('#product-form-title').textContent = 'Registrar juego';
    document.querySelector('#admin-product-submit').textContent = 'Registrar juego';
    document.querySelector('[data-action="cancel-product-edit"]').hidden = true;
    limpiarEstado('#product-status');
    if (enfocar) campos.nombre.focus();
  }

  function cargarProducto(id) {
    const producto = productos.buscar(id);

    if (!producto) {
      return;
    }

    const campos = obtenerCamposProducto();
    campos.id.value = producto.id;
    campos.nombre.value = producto.nombre;
    campos.categoria.value = producto.categoriaSlug;
    campos.descripcion.value = producto.descripcion;
    campos.precio.value = producto.precio;
    campos.stock.value = producto.stock;
    campos.activo.value = String(producto.activo);
    document.querySelector('#product-form-title').textContent = 'Editar juego';
    document.querySelector('#admin-product-submit').textContent = 'Guardar cambios';
    document.querySelector('[data-action="cancel-product-edit"]').hidden = false;
    limpiarEstado('#product-status');
    campos.nombre.focus();
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

  function leerFormularioProducto() {
    const campos = obtenerCamposProducto();
    return {
      id: campos.id.value,
      nombre: campos.nombre.value.trim(),
      categoriaSlug: campos.categoria.value,
      descripcion: campos.descripcion.value.trim(),
      precio: valorEntero(campos.precio),
      stock: valorEntero(campos.stock),
      activo: campos.activo.value === 'true'
    };
  }

  function validarFormularioProducto(valores) {
    if (valores.nombre.length < 2 || valores.nombre.length > 60) {
      return 'El nombre debe tener entre 2 y 60 caracteres.';
    }

    if (productos.existeNombre(valores.nombre, valores.id)) {
      return 'Ya existe un juego registrado con ese nombre.';
    }

    if (valores.descripcion.length < 10 || valores.descripcion.length > 220) {
      return 'La descripción debe tener entre 10 y 220 caracteres.';
    }

    if (!productos.listarCategorias().some((categoria) => categoria.slug === valores.categoriaSlug)) {
      return 'Selecciona una categoría válida.';
    }

    if (!Number.isInteger(valores.precio) || valores.precio < 0 || !Number.isInteger(valores.stock) || valores.stock < 0) {
      return 'Precio y disponibilidad deben ser números enteros iguales o mayores que cero.';
    }

    return '';
  }

  function conectarMantenedorProductos() {
    const formulario = document.querySelector('#admin-product-form');
    const tabla = document.querySelector('#admin-products-body');
    const botonNuevo = document.querySelector('[data-action="new-product"]');
    const botonCancelar = document.querySelector('[data-action="cancel-product-edit"]');

    if (!formulario || !tabla || !botonNuevo || !botonCancelar) {
      return;
    }

    botonNuevo.addEventListener('click', () => prepararNuevoProducto());
    botonCancelar.addEventListener('click', () => prepararNuevoProducto());

    tabla.addEventListener('click', (evento) => {
      const botonEditar = evento.target.closest('[data-edit-product]');
      const botonEstado = evento.target.closest('[data-toggle-product]');

      if (botonEditar) {
        cargarProducto(botonEditar.dataset.editProduct);
        return;
      }

      if (!botonEstado) {
        return;
      }

      const activo = botonEstado.dataset.nextActive === 'true';
      const producto = productos.cambiarEstadoProducto(botonEstado.dataset.toggleProduct, activo);

      if (!producto) {
        mostrarEstado('#product-status', 'No fue posible cambiar la publicación del juego.', 'error');
        return;
      }

      renderizarResumen();
      renderizarProductos();

      if (document.querySelector('#admin-product-id').value === producto.id) {
        document.querySelector('#admin-product-active').value = String(producto.activo);
      }

      mostrarEstado(
        '#product-status',
        producto.activo ? `${producto.nombre} volvió a publicarse.` : `${producto.nombre} fue quitado del catálogo.`,
        'success'
      );
    });

    formulario.addEventListener('submit', (evento) => {
      evento.preventDefault();
      limpiarEstado('#product-status');

      const valores = leerFormularioProducto();
      const error = validarFormularioProducto(valores);

      if (error) {
        mostrarEstado('#product-status', error, 'error');
        return;
      }

      const esEdicion = Boolean(valores.id);
      const producto = esEdicion
        ? productos.actualizarProducto(valores.id, valores)
        : productos.crearProducto(valores);

      if (!producto) {
        mostrarEstado('#product-status', 'No fue posible guardar el juego. Revisa los valores ingresados.', 'error');
        return;
      }

      renderizarResumen();
      renderizarProductos();

      if (esEdicion) {
        cargarProducto(producto.id);
        mostrarEstado('#product-status', `${producto.nombre} fue actualizado correctamente.`, 'success');
      } else {
        prepararNuevoProducto();
        mostrarEstado('#product-status', `${producto.nombre} fue registrado correctamente.`, 'success');
      }
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
        <a class="primary-link" href="${rutas.login ?? '/login/'}">Iniciar sesión</a>
      `;
      return;
    }

    guardia.hidden = true;
    contenido.hidden = false;
    renderizarResumen();
    renderizarProductos();
    renderizarUsuarios();
    prepararNuevoProducto(false);
    cargarUsuario(datos.listarUsuarios()[0].id);
    conectarMantenedorProductos();
    conectarMantenedorUsuarios(sesion);
  }

  iniciarAdministracion();
})();
