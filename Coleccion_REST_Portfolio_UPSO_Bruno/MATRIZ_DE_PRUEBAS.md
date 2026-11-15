# Matriz de pruebas

| Nº | Grupo | Caso | Método | Ruta | HTTP esperado |
|---:|---|---|---|---|---:|
| 1 | 01 Preparacion | Estado e iniciar datos de prueba | GET | `/` | 200 |
| 2 | 02 Catalogos | Consultar lenguajes | GET | `/lenguajes` | 200 |
| 3 | 02 Catalogos | Rechazar alta de lenguajes | POST | `/lenguajes` | 405 |
| 4 | 02 Catalogos | Rechazar modificacion de lenguajes | PUT | `/lenguajes` | 405 |
| 5 | 02 Catalogos | Consultar tecnologias | GET | `/tecnologias` | 200 |
| 6 | 02 Catalogos | Rechazar alta de tecnologias | POST | `/tecnologias` | 405 |
| 7 | 02 Catalogos | Rechazar modificacion de tecnologias | PUT | `/tecnologias` | 405 |
| 8 | 03 Usuarios | Registrar usuario A | POST | `/auth/register` | 201 |
| 9 | 03 Usuarios | Login usuario A | POST | `/auth/login` | 200 |
| 10 | 03 Usuarios | Registrar usuario B | POST | `/auth/register` | 201 |
| 11 | 03 Usuarios | Login usuario B | POST | `/auth/login` | 200 |
| 12 | 03 Usuarios | Rechazar email duplicado | POST | `/auth/register` | 409 |
| 13 | 03 Usuarios | Rechazar username duplicado | POST | `/auth/register` | 409 |
| 14 | 03 Usuarios | Rechazar email con tipo incorrecto | POST | `/auth/register` | 400 |
| 15 | 03 Usuarios | Rechazar nombre demasiado largo | POST | `/auth/register` | 400 |
| 16 | 03 Usuarios | Rechazar password con tipo incorrecto | POST | `/auth/register` | 400 |
| 17 | 03 Usuarios | Credenciales incorrectas | POST | `/auth/login` | 401 |
| 18 | 03 Usuarios | Perfil sin token | GET | `/auth/me` | 401 |
| 19 | 03 Usuarios | Perfil con token invalido | GET | `/auth/me` | 401 |
| 20 | 03 Usuarios | Perfil con token vencido - requiere helper | GET | `/auth/me` | 401 |
| 21 | 04 Perfil | Consultar perfil A | GET | `/auth/me` | 200 |
| 22 | 04 Perfil | Editar perfil A | PUT | `/auth/me` | 200 |
| 23 | 04 Perfil | Guardar perfil sin cambios | PUT | `/auth/me` | 200 |
| 24 | 04 Perfil | Login con email nuevo | POST | `/auth/login` | 200 |
| 25 | 04 Perfil | Email anterior ya no autentica | POST | `/auth/login` | 401 |
| 26 | 04 Perfil | Rechazar email de otra cuenta | PUT | `/auth/me` | 409 |
| 27 | 04 Perfil | Rechazar username de otra cuenta | PUT | `/auth/me` | 409 |
| 28 | 04 Perfil | Rechazar ID ajeno en el JSON | PUT | `/auth/me` | 400 |
| 29 | 04 Perfil | Verificar que B no cambio | GET | `/auth/me` | 200 |
| 30 | 05 Habilidades | A agrega lenguaje | POST | `/habilidades` | 201 |
| 31 | 05 Habilidades | A agrega tecnologia | POST | `/habilidades` | 201 |
| 32 | 05 Habilidades | Rechazar habilidad duplicada | POST | `/habilidades` | 409 |
| 33 | 05 Habilidades | A lista sus dos habilidades | GET | `/habilidades` | 200 |
| 34 | 05 Habilidades | Cambiar nivel de lenguaje A | PUT | `/habilidades/lenguaje/{{lang1}}` | 200 |
| 35 | 05 Habilidades | Guardar el mismo nivel | PUT | `/habilidades/lenguaje/{{lang1}}` | 200 |
| 36 | 05 Habilidades | B comienza sin habilidades | GET | `/habilidades` | 200 |
| 37 | 05 Habilidades | B no puede editar habilidad de A | PUT | `/habilidades/lenguaje/{{lang1}}` | 404 |
| 38 | 05 Habilidades | B no puede borrar habilidad de A | DELETE | `/habilidades/tecnologia/{{tech1}}` | 404 |
| 39 | 05 Habilidades | Comprobar habilidades A intactas | GET | `/habilidades` | 200 |
| 40 | 05 Habilidades | B registra el mismo lenguaje para si | POST | `/habilidades` | 201 |
| 41 | 05 Habilidades | B agrega su tecnologia | POST | `/habilidades` | 201 |
| 42 | 05 Habilidades | B elimina su propio lenguaje | DELETE | `/habilidades/lenguaje/{{lang1}}` | 200 |
| 43 | 05 Habilidades | B confirma borrado de su lenguaje | GET | `/habilidades` | 200 |
| 44 | 05 Habilidades | B restaura su lenguaje para la demo | POST | `/habilidades` | 201 |
| 45 | 05 Habilidades | Rechazar ID inexistente | POST | `/habilidades` | 400 |
| 46 | 05 Habilidades | Rechazar ID decimal | POST | `/habilidades` | 400 |
| 47 | 05 Habilidades | Rechazar ID booleano | POST | `/habilidades` | 400 |
| 48 | 05 Habilidades | Rechazar Tipo como objeto | POST | `/habilidades` | 400 |
| 49 | 05 Habilidades | Rechazar Nivel como lista | POST | `/habilidades` | 400 |
| 50 | 06 Proyectos | Crear proyecto completo A | POST | `/proyectos` | 201 |
| 51 | 06 Proyectos | Crear proyecto B | POST | `/proyectos` | 201 |
| 52 | 06 Proyectos | Listar proyectos exclusivos de A | GET | `/proyectos` | 200 |
| 53 | 06 Proyectos | Listar proyectos exclusivos de B | GET | `/proyectos` | 200 |
| 54 | 06 Proyectos | B no puede editar proyecto A | PUT | `/proyectos/{{project_a}}` | 404 |
| 55 | 06 Proyectos | B no puede borrar proyecto A | DELETE | `/proyectos/{{project_a}}` | 404 |
| 56 | 06 Proyectos | Actualizar proyecto A | PUT | `/proyectos/{{project_a}}` | 200 |
| 57 | 06 Proyectos | Solo cambiar lenguajes | PUT | `/proyectos/{{project_a}}` | 200 |
| 58 | 06 Proyectos | Restaurar dos lenguajes | PUT | `/proyectos/{{project_a}}` | 200 |
| 59 | 06 Proyectos | Solo cambiar tecnologias | PUT | `/proyectos/{{project_a}}` | 200 |
| 60 | 06 Proyectos | Restaurar dos tecnologias | PUT | `/proyectos/{{project_a}}` | 200 |
| 61 | 06 Proyectos | Solo cambiar enlaces | PUT | `/proyectos/{{project_a}}` | 200 |
| 62 | 07 Validaciones | Nombre como lista | POST | `/proyectos` | 400 |
| 63 | 07 Validaciones | Etapa como lista | POST | `/proyectos` | 400 |
| 64 | 07 Validaciones | Lenguajes vacios | POST | `/proyectos` | 400 |
| 65 | 07 Validaciones | Tecnologias vacias | POST | `/proyectos` | 400 |
| 66 | 07 Validaciones | Lenguajes omitidos | POST | `/proyectos` | 400 |
| 67 | 07 Validaciones | ID decimal en lenguajes | POST | `/proyectos` | 400 |
| 68 | 07 Validaciones | ID string en lenguajes | POST | `/proyectos` | 400 |
| 69 | 07 Validaciones | ID booleano en lenguajes | POST | `/proyectos` | 400 |
| 70 | 07 Validaciones | ID ajeno al catalogo | POST | `/proyectos` | 400 |
| 71 | 07 Validaciones | Tipo de enlace como objeto | POST | `/proyectos` | 400 |
| 72 | 07 Validaciones | Fecha como booleano | POST | `/proyectos` | 400 |
| 73 | 07 Validaciones | Dia inexistente | POST | `/proyectos` | 400 |
| 74 | 07 Validaciones | Campo adicional | POST | `/proyectos` | 400 |
| 75 | 07 Validaciones | PUT no permite quitar todos los lenguajes | PUT | `/proyectos/{{project_a}}` | 400 |
| 76 | 07 Validaciones | JSON raiz como lista | POST | `/proyectos` | 400 |
| 77 | 07 Validaciones | JSON mal escrito | POST | `/proyectos` | 400 |
| 78 | 07 Validaciones | ID de proyecto cero | PUT | `/proyectos/0` | 400 |
| 79 | 07 Validaciones | Verificar que el rechazo no borro relaciones | GET | `/proyectos` | 200 |
| 80 | 08 Acceso publico | Portfolio publico A sin token | GET | `/u/{{username_a}}` | 200 |
| 81 | 08 Acceso publico | Portfolio publico B sin token | GET | `/u/{{username_b}}` | 200 |
| 82 | 08 Acceso publico | Listado de proyectos sin token | GET | `/proyectos` | 401 |
| 83 | 08 Acceso publico | Alta proyecto sin token | POST | `/proyectos` | 401 |
| 84 | 08 Acceso publico | Edicion proyecto sin token | PUT | `/proyectos/{{project_a}}` | 401 |
| 85 | 08 Acceso publico | Borrado proyecto sin token | DELETE | `/proyectos/{{project_a}}` | 401 |
| 86 | 08 Acceso publico | Habilidades sin token | GET | `/habilidades` | 401 |
| 87 | 09 Limpieza | B elimina su propio proyecto | DELETE | `/proyectos/{{project_b}}` | 200 |
| 88 | 09 Limpieza | B confirma listado vacio | GET | `/proyectos` | 200 |
| 89 | 09 Limpieza | Eliminar cuenta QA A | DELETE | `/auth/me` | 200 |
| 90 | 09 Limpieza | Portfolio eliminado A no existe | GET | `/u/{{username_a}}` | 404 |
| 91 | 09 Limpieza | Eliminar cuenta QA B | DELETE | `/auth/me` | 200 |
| 92 | 09 Limpieza | Portfolio eliminado B no existe | GET | `/u/{{username_b}}` | 404 |
