'use strict';

document.addEventListener('DOMContentLoaded', () => {
  const pagina = document.querySelector('[data-external-games]');
  if (!pagina) return;

  const formulario = pagina.querySelector('[data-external-filters]');
  const grilla = pagina.querySelector('[data-external-grid]');
  const estado = pagina.querySelector('[data-external-status]');
  const contador = pagina.querySelector('[data-external-count]');
  const botonCargar = pagina.querySelector('[data-load-games]');
  const botonReintentar = pagina.querySelector('[data-external-retry]');
  const endpoint = pagina.dataset.endpoint;
  let controladorActivo = null;

  const agregarTexto = (elemento, texto) => {
    elemento.textContent = texto || '';
    return elemento;
  };

  const crearEtiqueta = (texto, clase) => {
    const etiqueta = document.createElement('span');
    etiqueta.className = clase;
    return agregarTexto(etiqueta, texto);
  };

  const crearTarjeta = (juego) => {
    const tarjeta = document.createElement('article');
    tarjeta.className = 'game-card external-game-card';
    tarjeta.dataset.externalId = String(juego.id || '');

    const imagen = document.createElement('img');
    imagen.src = juego.imagen || pagina.dataset.fallbackImage;
    imagen.alt = `Portada de ${juego.titulo}`;
    imagen.loading = 'lazy';
    imagen.referrerPolicy = 'no-referrer';
    tarjeta.appendChild(imagen);

    const informacion = document.createElement('div');
    informacion.className = 'game-info';

    const etiquetas = document.createElement('div');
    etiquetas.className = 'game-labels';
    etiquetas.appendChild(crearEtiqueta(juego.genero || 'Juego', 'tag'));
    etiquetas.appendChild(crearEtiqueta('Gratis', 'free-badge'));
    informacion.appendChild(etiquetas);

    informacion.appendChild(
      agregarTexto(document.createElement('h3'), juego.titulo),
    );
    informacion.appendChild(
      agregarTexto(
        document.createElement('p'),
        juego.descripcion || 'Consulta el sitio oficial para conocer más.',
      ),
    );

    const metadatos = document.createElement('dl');
    metadatos.className = 'external-meta';
    const valores = [
      ['Plataforma', juego.plataforma || 'No informada'],
      ['Editor', juego.editor || 'No informado'],
      ['Lanzamiento', juego.fecha_lanzamiento || 'No informado'],
    ];
    valores.forEach(([termino, valor]) => {
      metadatos.appendChild(agregarTexto(document.createElement('dt'), termino));
      metadatos.appendChild(agregarTexto(document.createElement('dd'), valor));
    });
    informacion.appendChild(metadatos);

    if (juego.sitio) {
      const enlace = agregarTexto(document.createElement('a'), 'Ver juego');
      enlace.className = 'button button-primary external-link';
      enlace.href = juego.sitio;
      enlace.target = '_blank';
      enlace.rel = 'noopener noreferrer';
      informacion.appendChild(enlace);
    }

    tarjeta.appendChild(informacion);
    return tarjeta;
  };

  const mostrarJuegos = (juegos) => {
    grilla.replaceChildren();
    juegos.forEach((juego) => grilla.appendChild(crearTarjeta(juego)));
    contador.textContent = `${juegos.length} resultados`;
    if (!juegos.length) {
      const vacio = agregarTexto(
        document.createElement('p'),
        'No se encontraron juegos para los filtros seleccionados.',
      );
      vacio.className = 'empty-state';
      grilla.appendChild(vacio);
    }
  };

  const cargarJuegos = async () => {
    if (controladorActivo) controladorActivo.abort();
    controladorActivo = new AbortController();

    const parametros = new URLSearchParams(new FormData(formulario));
    estado.textContent = 'Cargando juegos gratuitos…';
    estado.className = 'external-status loading';
    contador.textContent = '';
    botonReintentar.hidden = true;
    botonCargar.disabled = true;
    grilla.setAttribute('aria-busy', 'true');

    try {
      const respuesta = await fetch(`${endpoint}?${parametros.toString()}`, {
        headers: { Accept: 'application/json' },
        signal: controladorActivo.signal,
      });
      const datos = await respuesta.json().catch(() => ({}));
      if (!respuesta.ok) {
        throw new Error(datos.detalle || 'No fue posible consultar el servicio.');
      }

      mostrarJuegos(Array.isArray(datos.juegos) ? datos.juegos : []);
      estado.textContent = 'Catálogo externo actualizado correctamente.';
      estado.className = 'external-status success';
    } catch (error) {
      if (error.name === 'AbortError') return;
      grilla.replaceChildren();
      contador.textContent = '';
      estado.textContent = error.message || 'No fue posible cargar los juegos.';
      estado.className = 'external-status error';
      botonReintentar.hidden = false;
    } finally {
      botonCargar.disabled = false;
      grilla.setAttribute('aria-busy', 'false');
    }
  };

  formulario.addEventListener('submit', (event) => {
    event.preventDefault();
    cargarJuegos();
  });
  botonReintentar.addEventListener('click', cargarJuegos);
  cargarJuegos();
});
