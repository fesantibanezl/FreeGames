(() => {
  'use strict';

  const datos = window.FreeGamesData;
  const validacion = window.FreeGamesValidation;

  if (!datos) {
    console.warn('No se cargó la capa de datos simulados de FreeGames.');
    return;
  }

  let sesionActual = datos.obtenerSesion();

  function nombreRol(rol) {
    return rol === 'administrador' ? 'Administrador' : 'Cliente';
  }

  function actualizarNavegacion() {
    const haySesion = Boolean(sesionActual);

    document.querySelectorAll('[data-session="guest"]').forEach((elemento) => {
      elemento.hidden = haySesion;
    });

    document.querySelectorAll('[data-session="user"]').forEach((elemento) => {
      elemento.hidden = !haySesion;
    });

    document.querySelectorAll('[data-user-name]').forEach((elemento) => {
      elemento.textContent = haySesion ? sesionActual.usuario.nombreUsuario : '';
    });

    document.querySelectorAll('[data-user-role]').forEach((elemento) => {
      elemento.textContent = haySesion ? nombreRol(sesionActual.usuario.rol) : '';
    });
  }

  function conectarCierreSesion() {
    document.querySelectorAll('[data-action="logout"]').forEach((boton) => {
      boton.addEventListener('click', () => {
        datos.cerrarSesion();
        sesionActual = null;
        window.location.href = 'index.html';
      });
    });
  }

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

  function iniciarLogin() {
    const formulario = document.querySelector('#login-form');

    if (!formulario || !validacion) {
      return;
    }

    const acceso = document.querySelector('#acceso');
    const clave = document.querySelector('#clave-login');
    const estado = document.querySelector('#form-status');

    function validarAcceso() {
      if (acceso.value.trim() === '') {
        return validacion.mostrarError(acceso, 'Ingresa tu correo o nombre de usuario.');
      }

      return validacion.marcarValido(acceso);
    }

    function validarClaveLogin() {
      if (clave.value === '') {
        return validacion.mostrarError(clave, 'Ingresa tu contraseña.');
      }

      return validacion.marcarValido(clave);
    }

    formulario.addEventListener('submit', (evento) => {
      evento.preventDefault();
      limpiarEstado(estado);

      if (![validarAcceso(), validarClaveLogin()].every(Boolean)) {
        mostrarEstado(estado, 'Completa los campos marcados para iniciar sesión.', 'error');
        formulario.querySelector('.is-invalid')?.focus();
        return;
      }

      const usuario = datos.buscarUsuarioPorAcceso(acceso.value);

      if (!usuario || usuario.clave !== clave.value) {
        validacion.mostrarError(clave, 'Las credenciales ingresadas no son correctas.');
        mostrarEstado(estado, 'No fue posible iniciar sesión. Revisa tus credenciales.', 'error');
        clave.focus();
        return;
      }

      if (!usuario.activo) {
        mostrarEstado(estado, 'La cuenta está desactivada. Contacta al administrador.', 'error');
        return;
      }

      datos.crearSesion(usuario);
      sesionActual = datos.obtenerSesion();
      actualizarNavegacion();

      const destino = usuario.rol === 'administrador' ? 'perfil.html' : 'index.html';
      mostrarEstado(estado, `Sesión iniciada como ${nombreRol(usuario.rol)}. Redirigiendo…`, 'success');
      window.setTimeout(() => {
        window.location.href = destino;
      }, 900);
    });

    acceso.addEventListener('blur', validarAcceso);
    clave.addEventListener('blur', validarClaveLogin);

    acceso.addEventListener('input', () => {
      if (acceso.classList.contains('is-invalid')) validarAcceso();
    });

    clave.addEventListener('input', () => {
      if (clave.classList.contains('is-invalid')) validarClaveLogin();
    });
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

      // El mensaje es deliberadamente general para no revelar qué correos existen.
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

  function iniciarPerfil() {
    const formulario = document.querySelector('#perfil-form');

    if (!formulario || !validacion) {
      return;
    }

    const aviso = document.querySelector('#profile-guard');
    const tarjeta = document.querySelector('#profile-card');
    const estado = document.querySelector('#form-status');

    if (!sesionActual) {
      aviso.hidden = false;
      tarjeta.hidden = true;
      return;
    }

    const campos = {
      nombreCompleto: document.querySelector('#perfil-nombre-completo'),
      nombreUsuario: document.querySelector('#perfil-nombre-usuario'),
      correo: document.querySelector('#perfil-correo'),
      fechaNacimiento: document.querySelector('#perfil-fecha-nacimiento'),
      direccion: document.querySelector('#perfil-direccion'),
      rol: document.querySelector('#perfil-rol')
    };

    campos.fechaNacimiento.max = new Date().toISOString().split('T')[0];

    function cargarUsuario() {
      const usuario = datos.buscarUsuarioPorId(sesionActual.usuario.id);

      campos.nombreCompleto.value = usuario.nombreCompleto;
      campos.nombreUsuario.value = usuario.nombreUsuario;
      campos.correo.value = usuario.correo;
      campos.fechaNacimiento.value = usuario.fechaNacimiento;
      campos.direccion.value = usuario.direccion;
      campos.rol.value = nombreRol(usuario.rol);

      Object.values(campos).forEach((campo) => validacion.limpiarCampo(campo));
    }

    function validarNombreCompleto() {
      return validacion.validarCampo(campos.nombreCompleto, validacion.reglas.nombreCompleto);
    }

    function validarNombreUsuario() {
      const formatoValido = validacion.validarCampo(campos.nombreUsuario, validacion.reglas.nombreUsuario);

      if (formatoValido && datos.existeNombreUsuario(campos.nombreUsuario.value, sesionActual.usuario.id)) {
        return validacion.mostrarError(campos.nombreUsuario, 'Ese nombre de usuario pertenece a otra cuenta.');
      }

      return formatoValido;
    }

    function validarCorreo() {
      const formatoValido = validacion.validarCampo(campos.correo, validacion.reglas.correo);

      if (formatoValido && datos.existeCorreo(campos.correo.value, sesionActual.usuario.id)) {
        return validacion.mostrarError(campos.correo, 'Ese correo electrónico pertenece a otra cuenta.');
      }

      return formatoValido;
    }

    function validarFechaNacimiento() {
      return validacion.validarCampo(campos.fechaNacimiento, validacion.reglas.fechaNacimiento);
    }

    function validarDireccion() {
      if (campos.direccion.value.trim() === '') {
        validacion.limpiarCampo(campos.direccion);
        return true;
      }

      return validacion.validarCampo(campos.direccion, validacion.reglas.direccion);
    }

    const validacionesPerfil = new Map([
      [campos.nombreCompleto, validarNombreCompleto],
      [campos.nombreUsuario, validarNombreUsuario],
      [campos.correo, validarCorreo],
      [campos.fechaNacimiento, validarFechaNacimiento],
      [campos.direccion, validarDireccion]
    ]);

    cargarUsuario();
    tarjeta.hidden = false;
    formulario.hidden = false;

    formulario.addEventListener('submit', (evento) => {
      evento.preventDefault();
      limpiarEstado(estado);

      const resultados = [...validacionesPerfil.values()].map((validar) => validar());

      if (!resultados.every(Boolean)) {
        mostrarEstado(estado, 'Revisa los campos marcados antes de guardar.', 'error');
        formulario.querySelector('.is-invalid')?.focus();
        return;
      }

      const usuarioActualizado = datos.actualizarUsuario(sesionActual.usuario.id, {
        nombreCompleto: campos.nombreCompleto.value.trim(),
        nombreUsuario: campos.nombreUsuario.value.trim(),
        correo: campos.correo.value.trim().toLocaleLowerCase('es'),
        fechaNacimiento: campos.fechaNacimiento.value,
        direccion: campos.direccion.value.trim()
      });

      sesionActual = { ...sesionActual, usuario: usuarioActualizado };
      actualizarNavegacion();
      mostrarEstado(estado, 'Los datos del perfil se actualizaron correctamente.', 'success');
    });

    validacionesPerfil.forEach((validar, campo) => {
      campo.addEventListener('blur', validar);
      campo.addEventListener('input', () => {
        if (campo.classList.contains('is-invalid')) validar();
      });
    });

    formulario.addEventListener('reset', () => {
      window.setTimeout(() => {
        cargarUsuario();
        limpiarEstado(estado);
      }, 0);
    });
  }

  actualizarNavegacion();
  conectarCierreSesion();
  iniciarLogin();
  iniciarRecuperacion();
  iniciarPerfil();
})();
