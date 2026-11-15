# Verificación del paquete

- Cliente utilizado: Bruno CLI 4.3.0, formato OpenCollection YAML.
- Backend: código Flask de referencia con las mejoras de esta conversación.
- Persistencia de prueba: SQLite mediante adaptador; no MySQL real.
- Catálogo: mock configurado en el backend.
- Escenario completo: **92 peticiones aprobadas; 293/293 pruebas aprobadas**.
- Escenario sin token vencido configurado y conservando datos: **85 peticiones
  aprobadas, 7 omitidas; 274/274 pruebas ejecutadas aprobadas**. Las siete
  omitidas son el token vencido y las seis peticiones del grupo de limpieza.
- En el segundo escenario se verificó la conservación de dos usuarios, cuatro
  habilidades y dos proyectos.

Estos resultados corresponden a la validación del paquete generado, no a una
corrida contra la instalación de la usuaria. Para la entrega académica deben
repetirse las pruebas con MySQL en el proyecto y conservar esa evidencia.

No se incluyen logs con tokens ni respuestas completas de autenticación.
