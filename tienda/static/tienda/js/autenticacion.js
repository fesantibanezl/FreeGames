(() => {
  'use strict';

  const validacion = window.FreeGamesValidation;

  function mostrarEstado(elemento, mensaje, tipo) {
    elemento.textContent = mensaje;
    elemento.className = `form-status ${tipo}`;
    elemento.hidden = false;
    elemento.focus();
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
      if (!validarCorreo()) {
        evento.preventDefault();
        mostrarEstado(estado, 'Revisa el correo electrónico ingresado.', 'error');
        correo.focus();
      }
    });

    correo.addEventListener('blur', validarCorreo);
    correo.addEventListener('input', () => {
      if (correo.classList.contains('is-invalid')) validarCorreo();
    });
  }

  iniciarRecuperacion();
})();
