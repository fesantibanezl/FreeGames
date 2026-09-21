(() => {
  'use strict';

  const PATRONES = Object.freeze({
    nombre: /^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?:[ '\-][A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*$/,
    usuario: /^[A-Za-z0-9._-]+$/,
    correo: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    mayuscula: /[A-ZÁÉÍÓÚÜÑ]/,
    minuscula: /[a-záéíóúüñ]/,
    numero: /\d/,
    especial: /[^A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ\s]/
  });

  function obtenerError(campo) {
    return document.querySelector(`#error-${campo.id}`);
  }

  function mostrarError(campo, mensaje) {
    const error = obtenerError(campo);

    campo.classList.add('is-invalid');
    campo.classList.remove('is-valid');
    campo.setAttribute('aria-invalid', 'true');

    if (error) {
      error.textContent = mensaje;
    }

    return false;
  }

  function marcarValido(campo) {
    const error = obtenerError(campo);

    campo.classList.remove('is-invalid');
    campo.classList.add('is-valid');
    campo.setAttribute('aria-invalid', 'false');

    if (error) {
      error.textContent = '';
    }

    return true;
  }

  function limpiarCampo(campo) {
    campo.classList.remove('is-valid', 'is-invalid');
    campo.removeAttribute('aria-invalid');

    const error = obtenerError(campo);
    if (error) {
      error.textContent = '';
    }
  }

  function calcularEdad(fecha) {
    const hoy = new Date();
    const nacimiento = new Date(`${fecha}T00:00:00`);

    if (Number.isNaN(nacimiento.getTime())) {
      return Number.NaN;
    }

    let edad = hoy.getFullYear() - nacimiento.getFullYear();
    const diferenciaMeses = hoy.getMonth() - nacimiento.getMonth();

    if (diferenciaMeses < 0 || (diferenciaMeses === 0 && hoy.getDate() < nacimiento.getDate())) {
      edad -= 1;
    }

    return edad;
  }

  // Cada regla devuelve un mensaje; una cadena vacía significa que el dato es válido.
  const reglas = Object.freeze({
    nombreCompleto(valor) {
      const nombre = valor.trim();

      if (nombre === '') return 'Ingresa tu nombre completo.';
      if (nombre.length < 3 || nombre.length > 60) return 'El nombre debe tener entre 3 y 60 caracteres.';
      if (!PATRONES.nombre.test(nombre)) return 'Usa solamente letras, espacios, apóstrofes o guiones.';
      return '';
    },

    nombreUsuario(valor) {
      const usuario = valor.trim();

      if (usuario === '') return 'Ingresa un nombre de usuario.';
      if (usuario.length < 4 || usuario.length > 16) return 'El usuario debe tener entre 4 y 16 caracteres.';
      if (!PATRONES.usuario.test(usuario)) return 'Usa letras, números, puntos, guiones o guion bajo, sin espacios.';
      return '';
    },

    correo(valor) {
      const correo = valor.trim();

      if (correo === '') return 'Ingresa tu correo electrónico.';
      if (correo.length > 100 || !PATRONES.correo.test(correo)) return 'Ingresa un correo electrónico válido.';
      return '';
    },

    clave(valor) {
      if (valor === '') return 'Ingresa una contraseña.';
      if (valor.length < 8 || valor.length > 18) return 'La contraseña debe tener entre 8 y 18 caracteres.';
      if (/\s/.test(valor)) return 'La contraseña no puede contener espacios.';
      if (!PATRONES.mayuscula.test(valor)) return 'Incluye al menos una letra mayúscula.';
      if (!PATRONES.minuscula.test(valor)) return 'Incluye al menos una letra minúscula.';
      if (!PATRONES.numero.test(valor)) return 'Incluye al menos un número.';
      if (!PATRONES.especial.test(valor)) return 'Incluye al menos un carácter especial.';
      return '';
    },

    repetirClave(valor, claveOriginal) {
      if (valor === '') return 'Repite la contraseña.';
      if (valor !== claveOriginal) return 'Las contraseñas no coinciden.';
      return '';
    },

    fechaNacimiento(valor) {
      if (valor === '') return 'Ingresa tu fecha de nacimiento.';

      const nacimiento = new Date(`${valor}T00:00:00`);
      const hoy = new Date();
      hoy.setHours(0, 0, 0, 0);

      if (Number.isNaN(nacimiento.getTime())) return 'Ingresa una fecha válida.';
      if (nacimiento > hoy) return 'La fecha de nacimiento no puede ser futura.';
      if (calcularEdad(valor) < 13) return 'Debes tener al menos 13 años.';
      return '';
    },

    direccion(valor) {
      const direccion = valor.trim();

      if (direccion === '') return '';
      if (direccion.length < 10 || direccion.length > 160) return 'La dirección debe tener entre 10 y 160 caracteres.';
      return '';
    }
  });

  function validarCampo(campo, regla, ...argumentos) {
    const mensaje = regla(campo.value, ...argumentos);
    return mensaje ? mostrarError(campo, mensaje) : marcarValido(campo);
  }

  window.FreeGamesValidation = Object.freeze({
    reglas,
    validarCampo,
    mostrarError,
    marcarValido,
    limpiarCampo
  });

  const formulario = document.querySelector('#registro-form');

  if (!formulario) {
    return;
  }

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

  // Evita que el selector del navegador ofrezca fechas posteriores al día actual.
  campos.fechaNacimiento.max = new Date().toISOString().split('T')[0];

  function validarNombreCompleto() {
    return validarCampo(campos.nombreCompleto, reglas.nombreCompleto);
  }

  function validarNombreUsuario() {
    const formatoValido = validarCampo(campos.nombreUsuario, reglas.nombreUsuario);

    if (formatoValido && window.FreeGamesData?.existeNombreUsuario(campos.nombreUsuario.value)) {
      return mostrarError(campos.nombreUsuario, 'Ese nombre de usuario ya está registrado.');
    }

    return formatoValido;
  }

  function validarCorreo() {
    const formatoValido = validarCampo(campos.correo, reglas.correo);

    if (formatoValido && window.FreeGamesData?.existeCorreo(campos.correo.value)) {
      return mostrarError(campos.correo, 'Ese correo electrónico ya está registrado.');
    }

    return formatoValido;
  }

  function validarClave() {
    return validarCampo(campos.clave, reglas.clave);
  }

  function validarRepeticionClave() {
    return validarCampo(campos.repetirClave, reglas.repetirClave, campos.clave.value);
  }

  function validarFechaNacimiento() {
    return validarCampo(campos.fechaNacimiento, reglas.fechaNacimiento);
  }

  function validarDireccion() {
    if (campos.direccion.value.trim() === '') {
      limpiarCampo(campos.direccion);
      return true;
    }

    return validarCampo(campos.direccion, reglas.direccion);
  }

  const validaciones = new Map([
    [campos.nombreCompleto, validarNombreCompleto],
    [campos.nombreUsuario, validarNombreUsuario],
    [campos.correo, validarCorreo],
    [campos.clave, validarClave],
    [campos.repetirClave, validarRepeticionClave],
    [campos.fechaNacimiento, validarFechaNacimiento],
    [campos.direccion, validarDireccion]
  ]);

  formulario.addEventListener('submit', (evento) => {
    evento.preventDefault();
    estadoFormulario.hidden = true;

    const resultados = [...validaciones.values()].map((validar) => validar());

    if (!resultados.every(Boolean)) {
      estadoFormulario.textContent = 'Revisa los campos marcados antes de continuar.';
      estadoFormulario.className = 'form-status error';
      estadoFormulario.hidden = false;
      formulario.querySelector('.is-invalid')?.focus();
      return;
    }

    if (!window.FreeGamesData) {
      estadoFormulario.textContent = 'No fue posible guardar el registro en este navegador.';
      estadoFormulario.className = 'form-status error';
      estadoFormulario.hidden = false;
      return;
    }

    window.FreeGamesData.registrarUsuario({
      nombreCompleto: campos.nombreCompleto.value,
      nombreUsuario: campos.nombreUsuario.value,
      correo: campos.correo.value,
      clave: campos.clave.value,
      fechaNacimiento: campos.fechaNacimiento.value,
      direccion: campos.direccion.value
    });

    estadoFormulario.textContent = 'Cuenta creada correctamente. Ya puedes iniciar sesión.';
    estadoFormulario.className = 'form-status success';
    estadoFormulario.hidden = false;
    estadoFormulario.focus();
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
      validaciones.forEach((validar, campo) => limpiarCampo(campo));
      estadoFormulario.textContent = '';
      estadoFormulario.className = 'form-status';
      estadoFormulario.hidden = true;
    }, 0);
  });
})();
