# Semana 8 — diagnóstico y plan de trabajo

Actividad sumativa grupal «Desarrollando API REST». Este documento registra el
diagnóstico inicial y el avance de las cinco partes frente a las instrucciones,
la rúbrica y la guía de aprendizaje de la Semana 8. La línea base siguiente es
histórica; los resultados actuales se documentan en `PRUEBAS_SEMANA8.md`.

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

## Línea base comprobada el 4 de octubre de 2026, antes de la parte 2

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
2. **API y seguridad (implementado y confirmado en Git).** Se añadió una
   página cliente de ambas API, pruebas de token y permisos por recurso y CORS
   restringido para aplicaciones de otros orígenes. Sigue pendiente confirmar
   con el docente si categorías y juegos satisfacen la expresión «dos API».
3. **Dos servicios externos (implementado y confirmado en Git).** Se mantuvo
   FreeToGame y se integró GamerPower en `/descubrir/`; ambos cargan sin
   recarga, con filtros, caché, errores y atribución independientes. Las dos
   consultas reales devolvieron HTTP 200 el 4 de octubre de 2026.
4. **Verificación integral (completada; pendiente de commit).** Se creó el
   esquema local `FREEGAMES` que faltaba en `XEPDB1`, se aplicaron las
   migraciones y se comprobó la aplicación real con Oracle. Se revisaron
   flujos de negocio, validaciones, GRID de 12 columnas y vistas de 390,
   768 y 1440 px. Se corrigió el margen interior de `/explorar-api/` en móvil
   y se ejecutó de nuevo la suite completa.
5. **Entrega y colaboración.** Revisar participación real en Git, documentación
   y configuración segura; actualizar el enlace del repositorio, preparar
   `.zip`/`.7-zip` con código y ambos SQL, abrirlo para comprobarlo y solo
   entonces realizar el envío único en AVA.

## Riesgos que deben resolverse antes de la entrega

1. **Atendido en el paso 3:** GamerPower es un segundo proveedor público
   independiente; verificar de nuevo su disponibilidad antes del envío final.
2. **Resuelto en este equipo en el paso 4:** la instancia `XEPDB1` estaba
   disponible, pero no existía el esquema local `FREEGAMES`. Tras crearlo y
   aplicar migraciones, los flujos con Oracle funcionaron. En otro equipo hay
   que preparar su propia instancia y ejecutar `migrate`.
3. **Medio:** dos familias de endpoints pueden interpretarse como una sola API
   si no se demuestra y documenta cada recurso claramente. Confirmar la
   interpretación del docente si es posible.
4. **Atendido en el paso 2:** `/explorar-api/` consume las dos rutas propias
   con token y filtros sin recargar; debe incluirse en la demostración final.
5. **Pendiente para el paso 5:** la participación equitativa del equipo no se
   puede inferir de los autores locales; requiere evidencia real en Git. La
   visualización en tres tamaños quedó documentada en la parte 4.
6. **Antes de publicar:** revisar valores de desarrollo de la configuración
   (clave secreta, modo depuración y credenciales) y no presentar la
   configuración local como despliegue de producción.

La parte 4 no incluye commit automático, push, merge ni entrega en AVA. El
estudiante confirmará los cambios de cada parte antes de continuar.
