(() => {
  'use strict';

  // Estos datos se conservarán en el navegador hasta migrar sus mantenedores.
  const CLAVES = Object.freeze({
    usuarios: 'freegames_usuarios'
  });

  // El mantenedor de usuarios seguirá usando estos datos hasta su migración.
  const USUARIOS_DEMO = Object.freeze([
    {
      id: 'cliente-demo',
      nombreCompleto: 'Felipe Santibáñez',
      nombreUsuario: 'cliente',
      correo: 'cliente@freegames.cl',
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

    // Las credenciales y la sesión pertenecen ahora exclusivamente a Django.
    usuarios.forEach((usuario) => delete usuario.clave);
    eliminar('freegames_sesion');

    guardar(CLAVES.usuarios, usuarios);
    return usuarios;
  }

  function listarUsuarios() {
    return leer(CLAVES.usuarios, USUARIOS_DEMO);
  }

  function buscarUsuarioPorId(id) {
    return listarUsuarios().find((usuario) => usuario.id === id) ?? null;
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

  function obtenerSesion() {
    const sesionServidor = window.FreeGamesConfig?.session;

    if (!sesionServidor?.authenticated || !sesionServidor.usuario) {
      return null;
    }

    return {
      usuarioId: String(sesionServidor.usuario.id),
      usuario: copiar(sesionServidor.usuario)
    };
  }

  inicializarUsuarios();

  window.FreeGamesData = Object.freeze({
    listarUsuarios,
    buscarUsuarioPorId,
    actualizarUsuario,
    obtenerSesion
  });

  // Los módulos de catálogo y compras reutilizan este acceso en vez de tocar localStorage.
  window.FreeGamesStore = Object.freeze({ leer, guardar, eliminar });
})();
