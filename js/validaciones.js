const formulario = document.querySelector('#registro-form');

if (formulario) {
  const campos = {
    nombreCompleto: document.querySelector('#nombre-completo'),
    nombreUsuario: document.querySelector('#nombre-usuario'),
    correo: document.querySelector('#correo'),
    clave: document.querySelector('#clave'),
    repetirClave: document.querySelector('#repetir-clave'),
    fechaNacimiento: document.querySelector('#fecha-nacimiento'),
    direccion: document.querySelector('#direccion')
  };

  const estadoFormulario = document.querySelector('#form-status');
  const formatoCorreo = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const contieneNumero = /\d/;
  const contieneMayuscula = /[A-ZÁÉÍÓÚÑ]/;

  function mostrarError(campo, mensaje) {
    const error = document.querySelector(`#error-${campo.id}`);

    campo.classList.add('is-invalid');
    campo.classList.remove('is-valid');
    campo.setAttribute('aria-invalid', 'true');

    if (error) {
      error.textContent = mensaje;
    }

    return false;
  }

  function marcarValido(campo) {
    const error = document.querySelector(`#error-${campo.id}`);

    campo.classList.remove('is-invalid');
    campo.classList.add('is-valid');
    campo.removeAttribute('aria-invalid');

    if (error) {
      error.textContent = '';
    }

    return true;
  }

  function calcularEdad(fecha) {
    const hoy = new Date();
    const nacimiento = new Date(`${fecha}T00:00:00`);
    let edad = hoy.getFullYear() - nacimiento.getFullYear();
    const diferenciaMeses = hoy.getMonth() - nacimiento.getMonth();

    if (diferenciaMeses < 0 || (diferenciaMeses === 0 && hoy.getDate() < nacimiento.getDate())) {
      edad -= 1;
    }

    return edad;
  }

  function validarNombreCompleto() {
    if (campos.nombreCompleto.value.trim() === '') {
      return mostrarError(campos.nombreCompleto, 'Ingresa tu nombre completo.');
    }

    return marcarValido(campos.nombreCompleto);
  }

  function validarNombreUsuario() {
    if (campos.nombreUsuario.value.trim() === '') {
      return mostrarError(campos.nombreUsuario, 'Ingresa un nombre de usuario.');
    }

    return marcarValido(campos.nombreUsuario);
  }

  function validarCorreo() {
    const correo = campos.correo.value.trim();

    if (correo === '') {
      return mostrarError(campos.correo, 'Ingresa tu correo electrónico.');
    }

    if (!formatoCorreo.test(correo)) {
      return mostrarError(campos.correo, 'Ingresa un correo electrónico válido.');
    }

    return marcarValido(campos.correo);
  }

  function validarClave() {
    const clave = campos.clave.value;

    if (clave === '') {
      return mostrarError(campos.clave, 'Ingresa una contraseña.');
    }

    if (clave.length < 6 || clave.length > 18) {
      return mostrarError(campos.clave, 'La contraseña debe tener entre 6 y 18 caracteres.');
    }

    if (!contieneNumero.test(clave)) {
      return mostrarError(campos.clave, 'La contraseña debe contener al menos un número.');
    }

    if (!contieneMayuscula.test(clave)) {
      return mostrarError(campos.clave, 'La contraseña debe contener al menos una letra mayúscula.');
    }

    return marcarValido(campos.clave);
  }

  function validarRepeticionClave() {
    if (campos.repetirClave.value === '') {
      return mostrarError(campos.repetirClave, 'Repite la contraseña.');
    }

    if (campos.repetirClave.value !== campos.clave.value) {
      return mostrarError(campos.repetirClave, 'Las contraseñas no coinciden.');
    }

    return marcarValido(campos.repetirClave);
  }

  function validarFechaNacimiento() {
    const fecha = campos.fechaNacimiento.value;

    if (fecha === '') {
      return mostrarError(campos.fechaNacimiento, 'Ingresa tu fecha de nacimiento.');
    }

    if (calcularEdad(fecha) < 13) {
      return mostrarError(campos.fechaNacimiento, 'Debes tener al menos 13 años para registrarte.');
    }

    return marcarValido(campos.fechaNacimiento);
  }

  const validaciones = new Map([
    [campos.nombreCompleto, validarNombreCompleto],
    [campos.nombreUsuario, validarNombreUsuario],
    [campos.correo, validarCorreo],
    [campos.clave, validarClave],
    [campos.repetirClave, validarRepeticionClave],
    [campos.fechaNacimiento, validarFechaNacimiento]
  ]);

  formulario.addEventListener('submit', (evento) => {
    evento.preventDefault();
    estadoFormulario.hidden = true;

    const resultados = [...validaciones.values()].map((validar) => validar());
    const formularioValido = resultados.every(Boolean);

    if (!formularioValido) {
      estadoFormulario.textContent = 'Revisa los campos marcados antes de continuar.';
      estadoFormulario.className = 'form-status error';
      estadoFormulario.hidden = false;
      formulario.querySelector('.is-invalid')?.focus();
      return;
    }

    estadoFormulario.textContent = 'Formulario validado correctamente. El registro se conectará al servidor en una próxima etapa.';
    estadoFormulario.className = 'form-status success';
    estadoFormulario.hidden = false;
  });

  validaciones.forEach((validar, campo) => {
    campo.addEventListener('blur', validar);
    campo.addEventListener('input', () => {
      if (campo.classList.contains('is-invalid')) {
        validar();
      }

      if (campo === campos.clave && campos.repetirClave.value !== '') {
        validarRepeticionClave();
      }
    });
  });

  formulario.addEventListener('reset', () => {
    window.setTimeout(() => {
      formulario.querySelectorAll('.is-valid, .is-invalid').forEach((campo) => {
        campo.classList.remove('is-valid', 'is-invalid');
        campo.removeAttribute('aria-invalid');
      });

      formulario.querySelectorAll('.field-error').forEach((error) => {
        error.textContent = '';
      });

      estadoFormulario.textContent = '';
      estadoFormulario.className = 'form-status';
      estadoFormulario.hidden = true;
    }, 0);
  });
}
