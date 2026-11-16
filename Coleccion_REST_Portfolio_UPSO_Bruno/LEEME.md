# Colección REST — Portfolio UPSO

Colección nativa de Bruno en formato OpenCollection YAML. Incluye **92
peticiones** con comprobaciones automáticas para la versión del backend que
fuimos construyendo: perfil editable, habilidades de lenguajes y tecnologías,
catálogo configurable, selección mínima en proyectos y validaciones estrictas.

## 1. Preparar la aplicación

1. Iniciar MySQL desde Laragon.
2. Iniciar el backend habitual en `http://localhost:5000`.
3. Mantener funcionando el catálogo configurado: mock local, mock HTTP o API
   oficial adaptada. El catálogo debe ofrecer al menos dos lenguajes y dos
   tecnologías para el proyecto de demostración.

Los IDs se obtienen de `GET /lenguajes` y `GET /tecnologias`; no se fijan en 1,
2 o 6. El frontend no es necesario para ejecutar las pruebas REST.

## 2. Abrir la colección en Bruno

1. En Bruno, elegir **Open Collection / Abrir colección**.
2. Seleccionar la carpeta **Portfolio_UPSO_Bruno**, que contiene
   `opencollection.yml`. El ZIP es un contenedor para descargar: primero se extrae.
3. Seleccionar el entorno **Local**.
4. Revisar `base_url`, cuyo valor inicial es `http://localhost:5000`.
5. Abrir el Runner de la colección y ejecutar todos los grupos en orden,
   **secuencialmente**, comenzando por `01 Preparacion`.

La primera petición prepara las variables de prueba y nombres únicos para esa
corrida. Las siguientes capturan IDs y tokens automáticamente. Para ejecutar
peticiones dependientes por separado hay que haber completado antes su preparación.

## 3. Qué se prueba

| Grupo | Cobertura |
|---|---|
| 01 Preparacion | API disponible y variables nuevas para cada ejecución. |
| 02 Catalogos | Listados, categorías, rechazo de altas y modificaciones. |
| 03 Usuarios | Registro, login, duplicados, tipos inválidos, token ausente, inválido y vencido. |
| 04 Perfil | Consulta, edición, persistencia, email nuevo, duplicados y rechazo de ID ajeno. |
| 05 Habilidades | Lenguajes, tecnologías, nivel, duplicados, IDs inválidos y aislamiento. |
| 06 Proyectos | CRUD, relaciones múltiples, varios links del mismo tipo y aislamiento. |
| 07 Validaciones | Listas vacías, IDs incorrectos, etapas, enlaces, fechas y JSON inválido. |
| 08 Acceso publico | Ambos portfolios sin token y rechazo de operaciones privadas sin token. |
| 09 Limpieza | Borrado de los datos QA creados por la corrida, configurable. |

También se comprueba que `fecha_actualizacion` avance al modificar solo
lenguajes, tecnologías o enlaces. Hay pausas de 1,1 segundos antes de esas tres
peticiones para distinguir cambios cuando MySQL guarda segundos enteros.

Ver `MATRIZ_DE_PRUEBAS.md` para el listado completo y sus códigos HTTP esperados.

## 4. Cuentas y limpieza

La colección crea dos cuentas QA nuevas por ejecución, con emails únicos
`qa.a...@example.com` y `qa.b...@example.com`. El perfil A cambia su email y
username durante las pruebas. Los tokens válidos se guardan como variables
runtime y no se escriben en los archivos de la colección.

Por defecto, **`limpiar_al_final=true`**: el último grupo elimina esas dos
cuentas y sus datos. Todas las operaciones autenticadas usan los tokens de las
cuentas generadas por la propia corrida; no se utilizan tus cuentas habituales.

Para conservar los portfolios como datos de demostración, cambiar a:

```text
limpiar_al_final=false
```

La limpieza aparecerá como OMITIDA. Quedarán dos usuarios, cada uno con dos
habilidades y un proyecto. El proyecto A tendrá dos lenguajes, dos tecnologías
y cuatro enlaces. Cada corrida conservada agrega otro par de cuentas QA.

Para ingresar desde el frontend con los datos conservados, consultar el email
actual de A en la respuesta de `Editar perfil A`, y el de B en `Registrar
usuario B`. La contraseña de ambas cuentas de prueba es `PruebaUPSO2026!`.
No agregar manualmente valores de tokens de tus cuentas personales a la colección.

## 5. Probar un token verdaderamente vencido

Esta prueba necesita un JWT firmado con la misma clave del backend y con
`exp` en el pasado. Cambiar el texto de un token no lo convierte en un token
vencido válido: rompería su firma y probaría otro caso.

Se incluye **generar_token_vencido.py**. Para usarlo:

1. Conservar ese script junto a la carpeta `Portfolio_UPSO_Bruno`.
2. Abrir PowerShell en la carpeta **backend del proyecto**.
3. Ejecutar con el Python de su entorno virtual, reemplazando la ruta de ejemplo:

```powershell
.\.venv\Scripts\python.exe "C:\RUTA\coleccion_bruno\generar_token_vencido.py"
```

4. El script lee `Config.JWT_SECRET` localmente y configura únicamente un token
   ya vencido en el entorno `Local.yml`. No muestra la clave ni cambia el backend.
5. Abrir o recargar la colección y el entorno Local en Bruno. Ejecutar desde
   el principio. El caso vencido debe devolver **401** y `token_expired`.

Si no se ejecuta el helper, la petición del token vencido se **omite** con un
mensaje. Una petición omitida no demuestra que esa validación funcione. Para
completar esa evidencia hay que configurar el token y volver a ejecutar.

Si aparece `token_invalid` en lugar de `token_expired`, regenerarlo desde el
backend correcto, usando su configuración actual. No usar un JWT tomado de
otro proyecto ni reemplazar la clave del backend para hacer pasar la prueba.

## 6. Cómo leer los resultados

Cada petición comprueba el HTTP esperado y que la respuesta sea JSON. Los
casos funcionales también comprueban datos, relaciones, propietario o nivel.
Un resultado 400 esperado es una prueba correcta cuando el cuerpo enviado es
inválido; no todos los casos deben responder 200.

Si falla una prueba, revisar el código HTTP, el cuerpo de respuesta y la
terminal del backend. Se recomienda detener la corrida en el primer fallo.
La colección refleja las mejoras ya indicadas: un error puede señalar que
algún archivo, migración o validación quedó pendiente de aplicar en tu copia.

La limpieza del final depende de que la corrida llegue a ese grupo. Si se
interrumpe antes, podrían quedar cuentas QA de esa ejecución.

## 7. Alcance de la verificación entregada

La colección se ejecutó con **Bruno CLI 4.3.0**, contra el código Flask de
referencia, usando SQLite como sustituto de persistencia de MySQL en un
entorno aislado. La ejecución completa pasó **92 peticiones y 293 pruebas**,
incluido el token firmado vencido.

También se verificaron las ramas que omiten el token vencido sin configurar y
conservan datos de demostración. No se ejecutó contra tu MySQL ni en tu Bruno
Desktop. Esas pruebas deben hacerse en tu computadora antes de presentarla.

La colección prueba la API: no comprueba clics duplicados, estilos, formatos
visuales de fechas ni comportamiento del navegador. Tampoco sustituye UML o
documentación de las etapas del proyecto.

## Referencias oficiales utilizadas para el formato y los scripts:

- https://www.usebruno.com/opencollection
- https://docs.usebruno.com/testing/script/javascript-reference
