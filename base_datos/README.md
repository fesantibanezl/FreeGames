# Scripts de base de datos

FreeGames utiliza Oracle mediante el ORM y las migraciones de Django. El comando recomendado para construir todo el esquema, incluidas las tablas internas de autenticación y sesiones, es:

```powershell
python manage.py migrate
```

Los archivos SQL se incluyen como entregables revisables de la evaluación:

1. `01_estructura_oracle.sql` contiene las seis tablas propias del sistema, sus claves, restricciones, índices y relaciones. Requiere que la tabla `AUTH_USER` de Django ya exista.
2. `02_datos_iniciales.sql` registra o actualiza los dos roles, las dos cuentas de prueba, sus perfiles, cinco categorías y quince juegos. Puede ejecutarse nuevamente sin duplicar registros.

Si el esquema se crea con `migrate`, no es necesario ejecutar manualmente estos archivos porque las migraciones `0001` a `0004` realizan las mismas operaciones. Los scripts permiten al docente revisar la estructura y los datos usando SQL Developer o SQL*Plus.
