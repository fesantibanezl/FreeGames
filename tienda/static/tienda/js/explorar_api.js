'use strict';

document.addEventListener('DOMContentLoaded', () => {
  const pagina = document.querySelector('[data-api-explorer]');
  if (!pagina) return;

  const formularioAcceso = pagina.querySelector('[data-api-login]');
  const formularioFiltros = pagina.querySelector('[data-api-filters]');
  const contrasena = pagina.querySelector('#api-password');
  const estadoAcceso = pagina.querySelector('[data-api-access-status]');
  const estadoJuegos = pagina.querySelector('[data-api-games-status]');
  const categorias = pagina.querySelector('[data-api-categories-list]');
  const selectorCategoria = pagina.querySelector('#api-category');
  const listaJuegos = pagina.querySelector('[data-api-games-list]');
  const contador = pagina.querySelector('[data-api-count]');
  const botonAcceso = pagina.querySelector('[data-api-login-button]');
  const botonFiltrar = pagina.querySelector('[data-api-filter-button]');
  const botonLimpiar = pagina.querySelector('[data-api-clear]');
  let token = null;
  let controladorJuegos = null;
  let controladorCategorias = null;

  const cambiarEstado = (elemento, mensaje, tipo = '') => {
    elemento.textContent = mensaje;
    elemento.className = `api-status ${tipo}`.trim();
  };

  const consultar = async (url, signal) => {
    const respuesta = await fetch(url, {
      credentials: 'same-origin',
      cache: 'no-store',
      headers: {
        Accept: 'application/json',
        Authorization: `Token ${token}`,
      },
      signal,
    });
    if (respuesta.status === 401) {
      throw new Error('El token ya no es válido. Limpia el acceso y vuelve a conectar.');
    }
    if (!respuesta.ok) {
      throw new Error('No fue posible consultar la API propia. Intenta nuevamente.');
    }
    return respuesta.json();
  };

  const mostrarCategorias = (datos) => {
    categorias.replaceChildren();
    selectorCategoria.replaceChildren(new Option('Todas', ''));

    datos.forEach((categoria) => {
      const etiqueta = document.createElement('span');
      etiqueta.className = 'api-category-tag';
      etiqueta.textContent = categoria.nombre;
      categorias.appendChild(etiqueta);
      selectorCategoria.add(new Option(categoria.nombre, categoria.slug));
    });
    if (!datos.length) categorias.textContent = 'No hay categorías disponibles.';
  };

  const mostrarJuegos = (datos) => {
    listaJuegos.replaceChildren();
    contador.textContent = `${datos.length} juego${datos.length === 1 ? '' : 's'}`;

    if (!datos.length) {
      const vacio = document.createElement('p');
      vacio.className = 'empty-state';
      vacio.textContent = 'No hay juegos para los filtros seleccionados.';
      listaJuegos.appendChild(vacio);
      return;
    }

    datos.forEach((juego) => {
      const tarjeta = document.createElement('article');
      tarjeta.className = 'api-game-item';

      const titulo = document.createElement('h3');
      titulo.textContent = juego.nombre;
      tarjeta.appendChild(titulo);

      const detalles = document.createElement('p');
      const precio = juego.gratis ? 'Gratis' : `$${Number(juego.precio).toLocaleString('es-CL')}`;
      detalles.textContent = `${juego.categoria_nombre} · ${precio} · ${juego.activo ? 'Activo' : 'Inactivo'}`;
      tarjeta.appendChild(detalles);

      listaJuegos.appendChild(tarjeta);
    });
  };

  const cargarCategorias = async () => {
    controladorCategorias?.abort();
    controladorCategorias = new AbortController();
    categorias.textContent = 'Cargando categorías…';
    try {
      const datos = await consultar(pagina.dataset.categoriasUrl, controladorCategorias.signal);
      if (!Array.isArray(datos)) throw new Error('La API de categorías devolvió datos inesperados.');
      mostrarCategorias(datos);
    } catch (error) {
      if (error.name === 'AbortError') return;
      categorias.textContent = error.message;
    }
  };

  const cargarJuegos = async () => {
    if (!token) return;
    controladorJuegos?.abort();
    const controlador = new AbortController();
    controladorJuegos = controlador;
    const parametros = new URLSearchParams();
    for (const [nombre, valor] of new FormData(formularioFiltros)) {
      if (String(valor).trim()) parametros.set(nombre, String(valor).trim());
    }
    const url = `${pagina.dataset.juegosUrl}?${parametros.toString()}`;

    cambiarEstado(estadoJuegos, 'Consultando la API de juegos…', 'loading');
    botonFiltrar.disabled = true;
    listaJuegos.setAttribute('aria-busy', 'true');
    try {
      const datos = await consultar(url, controlador.signal);
      if (!Array.isArray(datos)) throw new Error('La API de juegos devolvió datos inesperados.');
      mostrarJuegos(datos);
      cambiarEstado(estadoJuegos, 'Resultados actualizados sin recargar la página.', 'success');
    } catch (error) {
      if (error.name === 'AbortError') return;
      mostrarJuegos([]);
      cambiarEstado(estadoJuegos, error.message, 'error');
    } finally {
      if (controladorJuegos === controlador) {
        botonFiltrar.disabled = !token;
        listaJuegos.setAttribute('aria-busy', 'false');
      }
    }
  };

  formularioAcceso.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!formularioAcceso.reportValidity()) return;

    botonAcceso.disabled = true;
    cambiarEstado(estadoAcceso, 'Validando credenciales…', 'loading');
    try {
      const respuesta = await fetch(pagina.dataset.tokenUrl, {
        method: 'POST',
        credentials: 'same-origin',
        cache: 'no-store',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: formularioAcceso.elements.username.value,
          password: contrasena.value,
        }),
      });
      const datos = await respuesta.json().catch(() => ({}));
      if (!respuesta.ok || !datos.token) {
        throw new Error('No se pudo obtener el token. Revisa tu contraseña.');
      }

      token = datos.token;
      formularioAcceso.hidden = true;
      botonLimpiar.hidden = false;
      botonFiltrar.disabled = false;
      cambiarEstado(estadoAcceso, 'Conectado con token. No se guarda en el navegador.', 'success');
      await Promise.all([cargarCategorias(), cargarJuegos()]);
    } catch (error) {
      cambiarEstado(estadoAcceso, error.message || 'No fue posible conectar.', 'error');
    } finally {
      contrasena.value = '';
      botonAcceso.disabled = false;
    }
  });

  formularioFiltros.addEventListener('submit', (event) => {
    event.preventDefault();
    cargarJuegos();
  });

  botonLimpiar.addEventListener('click', () => {
    controladorCategorias?.abort();
    controladorJuegos?.abort();
    token = null;
    formularioAcceso.hidden = false;
    botonLimpiar.hidden = true;
    botonFiltrar.disabled = true;
    contrasena.value = '';
    formularioFiltros.reset();
    selectorCategoria.replaceChildren(new Option('Todas', ''));
    categorias.textContent = 'Conecta tu cuenta para ver las categorías.';
    listaJuegos.replaceChildren();
    contador.textContent = '';
    cambiarEstado(estadoAcceso, 'Acceso eliminado de esta página.');
    cambiarEstado(estadoJuegos, 'Conecta tu cuenta para consultar juegos.');
  });
});
