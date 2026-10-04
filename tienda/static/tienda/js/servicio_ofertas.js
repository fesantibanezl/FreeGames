'use strict';

document.addEventListener('DOMContentLoaded', () => {
  const seccion = document.querySelector('[data-giveaways]');
  if (!seccion) return;

  const formulario = seccion.querySelector('[data-giveaway-filters]');
  const grilla = seccion.querySelector('[data-giveaway-grid]');
  const estado = seccion.querySelector('[data-giveaway-status]');
  const contador = seccion.querySelector('[data-giveaway-count]');
  const botonCargar = seccion.querySelector('[data-load-giveaways]');
  const botonReintentar = seccion.querySelector('[data-giveaway-retry]');
  let controladorActivo = null;

  const agregarTexto = (elemento, texto) => {
    elemento.textContent = texto || '';
    return elemento;
  };

  const crearTarjeta = (oferta) => {
    const tarjeta = document.createElement('article');
    tarjeta.className = 'game-card external-game-card';
    tarjeta.dataset.giveawayId = String(oferta.id || '');

    const imagen = document.createElement('img');
    imagen.src = oferta.imagen || seccion.dataset.fallbackImage;
    imagen.alt = `Portada de ${oferta.titulo}`;
    imagen.loading = 'lazy';
    imagen.referrerPolicy = 'no-referrer';
    tarjeta.appendChild(imagen);

    const informacion = document.createElement('div');
    informacion.className = 'game-info';
    const etiquetas = document.createElement('div');
    etiquetas.className = 'game-labels';
    etiquetas.appendChild(
      agregarTexto(document.createElement('span'), 'Oferta temporal'),
    );
    etiquetas.firstChild.className = 'tag';
    etiquetas.appendChild(
      agregarTexto(document.createElement('span'), 'Juego completo'),
    );
    etiquetas.lastChild.className = 'free-badge';
    informacion.appendChild(etiquetas);

    informacion.appendChild(
      agregarTexto(document.createElement('h3'), oferta.titulo),
    );
    informacion.appendChild(
      agregarTexto(
        document.createElement('p'),
        oferta.descripcion || 'Consulta los detalles en GamerPower.',
      ),
    );

    const metadatos = document.createElement('dl');
    metadatos.className = 'external-meta';
    const valores = [
      ['Plataformas', oferta.plataformas || 'No informadas'],
      ['Valor habitual', oferta.valor || 'No informado'],
      ['Vigencia', oferta.fecha_fin ? `Hasta ${oferta.fecha_fin.slice(0, 10)}` : 'No informada'],
    ];
    valores.forEach(([termino, valor]) => {
      metadatos.appendChild(agregarTexto(document.createElement('dt'), termino));
      metadatos.appendChild(agregarTexto(document.createElement('dd'), valor));
    });
    informacion.appendChild(metadatos);

    if (oferta.sitio) {
      const enlace = agregarTexto(
        document.createElement('a'),
        'Ver promoción en GamerPower',
      );
      enlace.className = 'button button-primary external-link';
      enlace.href = oferta.sitio;
      enlace.target = '_blank';
      enlace.rel = 'noopener noreferrer';
      informacion.appendChild(enlace);
    }

    tarjeta.appendChild(informacion);
    return tarjeta;
  };

  const mostrarOfertas = (ofertas) => {
    grilla.replaceChildren();
    ofertas.forEach((oferta) => grilla.appendChild(crearTarjeta(oferta)));
    contador.textContent = `${ofertas.length} promociones`;
    if (!ofertas.length) {
      const vacio = agregarTexto(
        document.createElement('p'),
        'No hay promociones vigentes para esta plataforma.',
      );
      vacio.className = 'empty-state';
      grilla.appendChild(vacio);
    }
  };

  const cargarOfertas = async () => {
    controladorActivo?.abort();
    const controlador = new AbortController();
    controladorActivo = controlador;
    const parametros = new URLSearchParams(new FormData(formulario));

    estado.textContent = 'Consultando promociones de GamerPower…';
    estado.className = 'external-status loading';
    contador.textContent = '';
    botonReintentar.hidden = true;
    botonCargar.disabled = true;
    grilla.setAttribute('aria-busy', 'true');

    try {
      const respuesta = await fetch(
        `${seccion.dataset.endpoint}?${parametros.toString()}`,
        {
          headers: { Accept: 'application/json' },
          signal: controlador.signal,
        },
      );
      const datos = await respuesta.json().catch(() => ({}));
      if (!respuesta.ok) {
        throw new Error(datos.detalle || 'No fue posible consultar las ofertas.');
      }
      if (!Array.isArray(datos.ofertas)) {
        throw new Error('El servicio devolvió datos inesperados.');
      }

      mostrarOfertas(datos.ofertas);
      estado.textContent = 'Promociones actualizadas sin recargar la página.';
      estado.className = 'external-status success';
    } catch (error) {
      if (error.name === 'AbortError') return;
      grilla.replaceChildren();
      contador.textContent = '';
      estado.textContent = error.message || 'No fue posible cargar las ofertas.';
      estado.className = 'external-status error';
      botonReintentar.hidden = false;
    } finally {
      if (controladorActivo === controlador) {
        botonCargar.disabled = false;
        grilla.setAttribute('aria-busy', 'false');
      }
    }
  };

  formulario.addEventListener('submit', (event) => {
    event.preventDefault();
    cargarOfertas();
  });
  botonReintentar.addEventListener('click', cargarOfertas);
  cargarOfertas();
});
