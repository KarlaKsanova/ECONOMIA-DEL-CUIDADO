# Contexto vigente para el equipo y Copilot

Objetivo: observatorio de economía del cuidado CDMX y vinculación B2B2C con
centros comunitarios. Secuencia: datos, evidencia, decisión, programa social.
Piloto territorial propuesto: Iztapalapa. ETL: 16 alcaldías desde el inicio.
No afirmar que hay convenio, participantes o piloto ejecutado sin evidencia.

## Estado y responsables

- Marlon: arquitectura, interfaz, matching, integración y despliegue.
- Karla: ETL/GIS, movilidad/CONAPO y plantilla empresarial simulada; las dos
  nuevas entregas siguen pendientes de recepción e integración.
- Azael: simuladores B2B/B2G, fórmulas y documento LaTeX; pendientes.

No implementar fórmulas financieras supuestas como sustituto de Azael ni
fabricar fuentes de movilidad/CONAPO. Ver docs/CONTRATOS.md antes de integrar.

## Reglas de implementación

- Entrada principal: app_dashboard.py; dependencias únicas en requirements.txt.
- UI sin SQL ni ETL. Servicios coordinan; dominio aplica reglas.
- Datos territoriales preparados fuera del ciclo de Streamlit.
- Demo sintético en memoria, separado de cualquier base operativa.
- Esquema v2 aditivo de centros, servicios por franja, solicitudes y vinculaciones.
- DATABASE_URL común para operaciones internas; jamás versionar credenciales.
- No habilitar operación real pública hasta completar autenticación, roles,
  privacidad, verificación institucional y seguimiento.
- Matching de referencia explicable: compatibilidad, distancia y capacidad;
  no afirmar entrenamiento supervisado ni impacto laboral validado.
- Distribuir cifras CDMX por alcaldía genera estimaciones, no observaciones.
- Cuidado sin trabajo de mercado no equivale a abandono laboral por cuidados.
- No mezclar las horas ENUT con ENASIC o con otro ámbito de población.
- Recomendación no significa plaza confirmada ni horas efectivamente liberadas.

## Trabajo colaborativo

Ramas por cambio, pruebas antes de integrar, PR hacia main. El despliegue
inicial de Streamlit requiere administración del repositorio (Karla);
los colaboradores continúan subiendo código según permisos de GitHub.
