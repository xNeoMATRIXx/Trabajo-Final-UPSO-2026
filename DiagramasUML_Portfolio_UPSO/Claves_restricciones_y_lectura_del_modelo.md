# Claves, restricciones y lectura del modelo

**MODELO DE DATOS**

## Claves compuestas

`habilidades`: (`usuario_id`, `tipo`, `elemento_id`). `proyecto_lenguaje`: (`proyecto_id`, `lenguaje_id`). `proyecto_tecnologia`: (`proyecto_id`, `tecnologia_id`). Evitan repetir una relación. Un usuario puede registrar lenguaje 1 y tecnología 1 porque `tipo` diferencia los catálogos.

## Propiedad e integridad referencial

`usuarios` es el padre de `habilidades` y `proyectos`. `proyectos` es el padre de `proyecto_lenguaje`, `proyecto_tecnologia` y `proyecto_links`. En cada relación física, el hijo pertenece exactamente a un padre y el padre puede tener cero o muchos hijos.

## Eliminación en cascada

Las cinco FK usan `ON DELETE CASCADE`. Eliminar un usuario elimina sus habilidades y proyectos; eliminar un proyecto elimina sus filas de lenguajes, tecnologías y enlaces. Las operaciones no modifican los catálogos externos.

## Fechas y actualización

`created_at`, `fecha_creacion` y `fecha_actualizacion` admiten `NULL` y tienen `CURRENT_TIMESTAMP` como valor por defecto. `fecha_actualizacion` también tiene `ON UPDATE CURRENT_TIMESTAMP`. El endpoint trabajado actualiza explícitamente esa marca cuando se cambian solo relaciones. `fecha_finalizacion` y `fecha_deadline` son `DATE` opcionales.

## Enumeraciones SQL

### TipoHabilidad

`lenguaje`, `tecnologia`

### NivelDominio

`basico`, `intermedio`, `avanzado`

### EtapaProyecto

`formulacion`, `modelado`, `implementacion`, `testing`, `produccion`, `mantenimiento`

### TipoLink

`repositorio`, `demo`, `documentacion`, `video`, `otro`

## Referencias a catálogos

`elemento_id`, `lenguaje_id` y `tecnologia_id` no tienen FK SQL hacia tablas de catálogo locales. El backend valida los IDs contra el catálogo adecuado. `categoria` es un atributo de Tecnología en el adaptador/mock actual; no existe una tabla `categorias`. El modelo se revisará al integrar la API oficial.

## Reglas de proyectos y habilidades

Cada proyecto exige uno o más lenguajes y una o más tecnologías al crear y editar. Habilidad utiliza un único catálogo según `tipo`: `{xor}`. El propietario se obtiene del token. `proyecto_links` permite varios enlaces del mismo tipo; cada fila tiene su propio `id`.