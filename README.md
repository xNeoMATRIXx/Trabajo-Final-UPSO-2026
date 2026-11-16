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