(() => {
  'use strict';

  // Estas claves mantienen los datos simulados separados del resto del sitio.
  const CLAVES = Object.freeze({
    usuarios: 'freegames_usuarios',
    sesion: 'freegames_sesion'
  });

  // Las cuentas permiten probar los privilegios sin depender todavía de un servidor.
  const USUARIOS_DEMO = Object.freeze([
    {
      id: 'cliente-demo',
      nombreCompleto: 'Felipe Santibáñez',
      nombreUsuario: 'cliente',
      correo: 'cliente@freegames.cl',
      clave: 'Cliente#2026',
      fechaNacimiento: '2000-06-15',
      direccion: 'Av. Providencia 1234, Santiago',
      rol: 'cliente',
      activo: true
    },
    {
      id: 'administrador-demo',
      nombreCompleto: 'Diego Ramírez',
      nombreUsuario: 'admin',
      correo: 'admin@freegames.cl',
      clave: 'Admin#2026',
      fechaNacimiento: '1995-03-20',
      direccion: 'Av. Libertador 450, Santiago',
      rol: 'administrador',
      activo: true
    }
  ]);

  // La memoria temporal mantiene la página funcional si el navegador bloquea el almacenamiento.
  const almacenamientoTemporal = new Map();
  let almacenamientoLocalDisponible = true;

  function copiar(valor) {
    return JSON.parse(JSON.stringify(valor));
  }

  function leer(clave, respaldo) {
    if (almacenamientoLocalDisponible) {
      try {
        const contenido = localStorage.getItem(clave);
        return contenido ? JSON.parse(contenido) : copiar(respaldo);
      } catch (error) {
        almacenamientoLocalDisponible = false;
        console.warn('El navegador bloqueó el almacenamiento local; se usará memoria temporal.', error);
      }
    }

    const contenidoTemporal = almacenamientoTemporal.get(clave);
    return contenidoTemporal ? JSON.parse(contenidoTemporal) : copiar(respaldo);
  }

  function guardar(clave, valor) {
    const contenido = JSON.stringify(valor);

    if (almacenamientoLocalDisponible) {
      try {
        localStorage.setItem(clave, contenido);
        return true;
      } catch (error) {
        almacenamientoLocalDisponible = false;
        console.warn('El navegador bloqueó el almacenamiento local; se usará memoria temporal.', error);
      }
    }

    almacenamientoTemporal.set(clave, contenido);
    return true;
  }

  function eliminar(clave) {
    if (almacenamientoLocalDisponible) {
      try {
        localStorage.removeItem(clave);
        return true;
      } catch (error) {
        almacenamientoLocalDisponible = false;
        console.warn('El navegador bloqueó el almacenamiento local; se usará memoria temporal.', error);
      }
    }

    almacenamientoTemporal.delete(clave);
    return true;
  }

  function normalizar(valor) {
    return String(valor ?? '').trim().toLocaleLowerCase('es');
  }

  function inicializarUsuarios() {
    const usuariosGuardados = leer(CLAVES.usuarios, []);
    const usuarios = Array.isArray(usuariosGuardados) ? usuariosGuardados : [];

    // Se agregan solo las cuentas demo que aún no existen para conservar cambios del usuario.
    USUARIOS_DEMO.forEach((usuarioDemo) => {
      const usuarioGuardado = usuarios.find((usuario) => usuario.id === usuarioDemo.id);

      if (!usuarioGuardado) {
        usuarios.push(copiar(usuarioDemo));
      }

      // Actualiza el nombre demo anterior sin sobrescribir perfiles editados por el usuario.
      if (usuarioGuardado?.id === 'cliente-demo' && usuarioGuardado.nombreCompleto === 'Camila Torres') {
        usuarioGuardado.nombreCompleto = usuarioDemo.nombreCompleto;
      }
    });

    guardar(CLAVES.usuarios, usuarios);
    return usuarios;
  }

  function listarUsuarios() {
    return leer(CLAVES.usuarios, USUARIOS_DEMO);
  }

  function buscarUsuarioPorId(id) {
    return listarUsuarios().find((usuario) => usuario.id === id) ?? null;
  }

  function buscarUsuarioPorAcceso(acceso) {
    const valorBuscado = normalizar(acceso);

    return listarUsuarios().find((usuario) => (
      normalizar(usuario.correo) === valorBuscado
      || normalizar(usuario.nombreUsuario) === valorBuscado
    )) ?? null;
  }

  function existeNombreUsuario(nombreUsuario, idExcluido = '') {
    const valorBuscado = normalizar(nombreUsuario);
    return listarUsuarios().some((usuario) => (
      usuario.id !== idExcluido && normalizar(usuario.nombreUsuario) === valorBuscado
    ));
  }

  function existeCorreo(correo, idExcluido = '') {
    const valorBuscado = normalizar(correo);
    return listarUsuarios().some((usuario) => (
      usuario.id !== idExcluido && normalizar(usuario.correo) === valorBuscado
    ));
  }

  function registrarUsuario(datos) {
    const usuarios = listarUsuarios();
    const usuario = {
      id: `usuario-${Date.now()}`,
      nombreCompleto: datos.nombreCompleto.trim(),
      nombreUsuario: datos.nombreUsuario.trim(),
      correo: datos.correo.trim().toLocaleLowerCase('es'),
      // La clave se guarda solo para esta simulación FrontEnd; el backend deberá protegerla.
      clave: datos.clave,
      fechaNacimiento: datos.fechaNacimiento,
      direccion: datos.direccion.trim(),
      rol: 'cliente',
      activo: true
    };

    usuarios.push(usuario);
    guardar(CLAVES.usuarios, usuarios);
    return copiar(usuario);
  }

  function actualizarUsuario(id, cambios) {
    const usuarios = listarUsuarios();
    const posicion = usuarios.findIndex((usuario) => usuario.id === id);

    if (posicion === -1) {
      return null;
    }

    usuarios[posicion] = { ...usuarios[posicion], ...cambios, id };
    guardar(CLAVES.usuarios, usuarios);
    return copiar(usuarios[posicion]);
  }

  function crearSesion(usuario) {
    const sesion = {
      usuarioId: usuario.id,
      rol: usuario.rol,
      iniciadaEn: new Date().toISOString()
    };

    guardar(CLAVES.sesion, sesion);
    return copiar(sesion);
  }

  function obtenerSesion() {
    const sesion = leer(CLAVES.sesion, null);

    if (!sesion?.usuarioId) {
      return null;
    }

    const usuario = buscarUsuarioPorId(sesion.usuarioId);

    if (!usuario || !usuario.activo) {
      cerrarSesion();
      return null;
    }

    return { ...sesion, usuario };
  }

  function cerrarSesion() {
    eliminar(CLAVES.sesion);
  }

  inicializarUsuarios();

  window.FreeGamesData = Object.freeze({
    listarUsuarios,
    buscarUsuarioPorId,
    buscarUsuarioPorAcceso,
    existeNombreUsuario,
    existeCorreo,
    registrarUsuario,
    actualizarUsuario,
    crearSesion,
    obtenerSesion,
    cerrarSesion
  });

  // Los módulos de catálogo y compras reutilizan este acceso en vez de tocar localStorage.
  window.FreeGamesStore = Object.freeze({ leer, guardar, eliminar });
})();
