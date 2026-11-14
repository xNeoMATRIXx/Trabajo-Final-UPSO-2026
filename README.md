# Portfolio Devs

Proyecto Final Grupal de Proyecto Informático (UPSO). La aplicación busca reunir portfolios de desarrolladores y sus proyectos.

## Estructura

- `backend/`: API REST desarrollada con Flask y persistencia en MySQL.
- `frontend/`: cliente web con HTML, CSS y JavaScript.
- `backend/sql/schema.sql`: creación del esquema y las tablas de la aplicación.

## Funcionalidades actuales

- Registro e inicio de sesión con tokens JWT.
- Administración de habilidades tecnológicas y proyectos propios.
- Asociación de lenguajes, tecnologías y enlaces a los proyectos.
- Consulta pública del portfolio de un usuario.
- Catálogos de lenguajes y tecnologías servidos actualmente desde listas estáticas del backend.

## Tecnologías

- Python, Flask y Flask-CORS.
- MySQL.
- HTML, CSS y JavaScript.
- JWT y bcrypt para autenticación y contraseñas.

## Puesta en marcha

1. Crear la base de datos ejecutando `backend/sql/schema.sql` en MySQL.
2. Desde `backend/`, crear y activar un entorno virtual, e instalar las dependencias:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

3. Configurar localmente las variables de entorno utilizadas por `backend/config.py` para MySQL, JWT y Flask. No publicar claves ni contraseñas.
4. Iniciar la API desde `backend/`:

   ```powershell
   python app.py
   ```

   Por defecto, Flask escucha en el puerto `5000`.
5. Servir `frontend/` con un servidor web local y abrir la aplicación en el navegador.

## Próximos puntos a revisar

Tomando los checklists adjuntos como referencia informativa, conviene priorizar la integración de los catálogos con la API del profesor (incluidos su mecanismo de acceso y el manejo de errores), el soporte de lenguajes en las habilidades, las validaciones requeridas para los proyectos y la edición del perfil propio. También se deben verificar los entregables complementarios, como datos de prueba, diagramas UML y colección de pruebas de Bruno, contra la consigna vigente.

## Historial

- Primer commit del repositorio: **14 de noviembre de 2026** (`b1607c6`).
- En el backend el archivo env.txt debe ser renombrado a .env