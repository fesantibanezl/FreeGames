(() => {
  'use strict';

  const validacion = window.FreeGamesValidation;

  function mostrarEstado(elemento, mensaje, tipo) {
    elemento.textContent = mensaje;
    elemento.className = `form-status ${tipo}`;
    elemento.hidden = false;
    elemento.focus();
  }

  function limpiarEstado(elemento) {
    elemento.textContent = '';
    elemento.className = 'form-status';
    elemento.hidden = true;
  }

  function iniciarRecuperacion() {
    const formulario = document.querySelector('#recuperar-form');

    if (!formulario || !validacion) {
      return;
    }

    const correo = document.querySelector('#correo-recuperacion');
    const estado = document.querySelector('#form-status');

    function validarCorreo() {
      return validacion.validarCampo(correo, validacion.reglas.correo);
    }

    formulario.addEventListener('submit', (evento) => {
      evento.preventDefault();
      limpiarEstado(estado);

      if (!validarCorreo()) {
        mostrarEstado(estado, 'Revisa el correo electrónico ingresado.', 'error');
        correo.focus();
        return;
      }

      // El mensaje es general para no revelar qué correos existen.
      mostrarEstado(
        estado,
        'Si el correo está registrado, recibirás instrucciones de recuperación. Este envío es una simulación.',
        'success'
      );
    });

    correo.addEventListener('blur', validarCorreo);
    correo.addEventListener('input', () => {
      if (correo.classList.contains('is-invalid')) validarCorreo();
    });
  }

  iniciarRecuperacion();
})();
