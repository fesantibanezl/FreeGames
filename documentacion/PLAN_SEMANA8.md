# Semana 8 — diagnóstico y plan de trabajo

Actividad sumativa grupal «Desarrollando API REST». Este documento registra el
**paso 1 de 5**: el estado inicial de FreeGames frente a las instrucciones,
la rúbrica y la guía de aprendizaje de la Semana 8. No se modificó código de
la aplicación durante este paso.

## Fuentes y entrega solicitada

- `PGY3221_Exp3_Instrucciones_especificas_actividad_con_encargo_S8.docx`:
  exige al menos dos API REST propias, dos servicios públicos externos dentro
  de la aplicación, y conservar los requisitos funcionales anteriores.
- `PGY3221_Exp3_rubrica_actividad_con_encargo_S8.docx`: dos API (27,5 puntos),
  dos servicios externos (27,5), token en ambas API (15), FrontEnd/BackEnd (20)
  y colaboración en Git (10).
- `PGY3221_Exp3_guia_de_aprendizaje_S8.docx`: IL5 (Git), IL10 (servicio externo
  mostrado sin recargar), IL11 (API propia consumible por la aplicación, con
  filtros y acceso seguro).
- Texto de la actividad en AVA proporcionado por el estudiante: Parte I en
  `.zip` o `.7-zip` con código fuente, script de estructura de base de datos y
  script de datos iniciales; Parte II con un `.txt` que contenga el enlace al
  repositorio dentro del mismo comprimido. La entrega es grupal, vale 25 % de
  la asignatura y dispone de un intento.

## Estado comprobado el 4 de octubre de 2026

| Criterio | Evidencia encontrada | Estado y acción pendiente |
| --- | --- | --- |
| Dos API REST propias (27,5) | `/api/categorias/` y `/api/juegos/` tienen colección, detalle, serializadores y operaciones CRUD. Juegos dispone de filtros por nombre, categoría, estado y gratuidad. | Implementado como dos familias de recursos dentro de una aplicación `api`. Hay que documentarlas y probarlas por separado; confirmar con el docente si esta separación satisface «dos API propias». La interfaz actual no demuestra consumo de estas rutas. |
| Dos servicios externos (27,5) | `/descubrir/` consume FreeToGame mediante un adaptador Django y `fetch()` sin recarga. Hay pruebas automatizadas con respuestas simuladas. | Falta el segundo proveedor público. El funcionamiento en vivo de FreeToGame no quedó verificado en este diagnóstico. |
| Token en ambas API (15) | `/api/token/`, `TokenAuthentication` global y permiso de consulta autenticada/escritura administrativa sobre ambos recursos. | La base está implementada. Ampliar las pruebas explícitas de acceso sin token, token inválido y roles para **cada** recurso; comprobar el uso desde un cliente externo. |
| FrontEnd y BackEnd (20) | Django, dos roles, registro, login, recuperación de contraseña, perfil, CRUD, carrito, compra simulada, inventario e historial. Hay seis tablas propias en `01_estructura_oracle.sql` y carga inicial en `02_datos_iniciales.sql`. Se emplea Bootstrap y hay puntos de quiebre CSS. | Las 71 pruebas pasan con SQLite y `manage.py check` no reporta problemas. Falta revisar visualmente tres tamaños y la aplicación del GRID de 12 columnas en todas las pantallas relevantes. La conexión Oracle local no se pudo verificar: respondió `ORA-01017` (credenciales inválidas). |
| Colaboración en Git (10) | Repositorio `origin` configurado; ramas y commits históricos. Rama de esta semana: `codex/semana-8`. | El historial local muestra dos nombres de autor con **el mismo correo**, por lo que no demuestra participación equitativa de varios integrantes. La evidencia debe corresponder a trabajo real del equipo; no fabricar commits. |
| Entrega | Existen los dos SQL y `ENLACE_GITHUB.txt`. | El `.txt` actual conserva referencias a la Semana 6: actualizarlo para la entrega final y comprobar el contenido del comprimido antes del único envío. |

## Comprobaciones realizadas

- Rama inicial `main` limpia y sincronizada con `origin/main`; se creó
  `codex/semana-8` antes de editar este documento.
- `FREEGAMES_USE_SQLITE=1` + `python manage.py check`: **sin problemas**.
- `FREEGAMES_USE_SQLITE=1` + `python manage.py test`: **71 pruebas correctas**.
- `python manage.py showmigrations tienda --database default` con la
  configuración Oracle predeterminada: **no completó**, error `ORA-01017`.
  No había variables `FREEGAMES_DB_NAME`, `FREEGAMES_DB_USER` ni
  `FREEGAMES_DB_PASSWORD` definidas en la sesión de diagnóstico. Esto indica
  un problema de autenticación local; no demuestra un defecto de las
  migraciones ni de los scripts SQL.
- No se hizo una prueba visual en navegador ni una consulta en vivo a los
  servicios externos. Las pruebas automatizadas usan respuestas simuladas.

## Secuencia acordada: una parte a la vez

1. **Diagnóstico (completado en este documento).** Registrar estado y riesgos
   antes de modificar la aplicación.
2. **API y seguridad.** Demostrar dos recursos API independientes, CRUD,
   filtros, consumo desde cliente, token y permisos con pruebas completas.
3. **Dos servicios externos.** Mantener FreeToGame e integrar un segundo
   proveedor relacionado con videojuegos, mostrar ambos sin recarga y
   gestionar errores, límites y atribución.
4. **Verificación integral.** Resolver la conexión Oracle local, revisar
   flujos de negocio, validaciones, GRID de 12 columnas y tres tamaños de
   pantalla; corregir regresiones y volver a ejecutar las pruebas.
5. **Entrega y colaboración.** Revisar participación real en Git, documentación
   y configuración segura; actualizar el enlace del repositorio, preparar
   `.zip`/`.7-zip` con código y ambos SQL, abrirlo para comprobarlo y solo
   entonces realizar el envío único en AVA.

## Riesgos que deben resolverse antes de la entrega

1. **Alto:** falta el segundo servicio externo, indispensable para el máximo
   puntaje del criterio correspondiente.
2. **Alto:** Oracle rechaza las credenciales locales; la validación SQLite no
   sustituye la demostración con Oracle exigida por la actividad.
3. **Medio:** dos familias de endpoints pueden interpretarse como una sola API
   si no se demuestra y documenta cada recurso claramente. Confirmar la
   interpretación del docente si es posible.
4. **Medio:** la guía IL11 pide consumo de una API propia por la aplicación;
   actualmente las páginas Django consultan los modelos directamente y el
   JavaScript solo consulta el adaptador de FreeToGame.
5. **Medio:** la participación equitativa del equipo y la visualización en
   tres tamaños aún no están evidenciadas de forma suficiente.
6. **Antes de publicar:** revisar valores de desarrollo de la configuración
   (clave secreta, modo depuración y credenciales) y no presentar la
   configuración local como despliegue de producción.

Este paso no incluye commits, push, merge ni entrega en AVA. Cada parte se
revisará antes de continuar con la siguiente.
