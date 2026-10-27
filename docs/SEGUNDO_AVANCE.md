# Evidencia del segundo avance

| Componente | Estado en esta migración | Pendiente |
|---|---|---|
| Arquitectura | Paquete modular y entrada única | Integrar revisión del equipo |
| ETL | 16 alcaldías y reporte de calidad | Validar fuentes/alcances con Karla |
| Observatorio | Se conserva mapa y comparativos | Auditoría completa de indicadores |
| Matching | Demo de centros, horarios, tipos y cupos | Evaluación comparativa y piloto real |
| Persistencia | Esquema v2 aditivo y confirmación transaccional interna | Autenticación, seguimiento, migración de registros y prueba PostgreSQL |
| Movilidad/CONAPO | Contrato y estado pendiente | Entrega de Karla |
| Plantilla empresarial | Contrato y estado pendiente | Entrega de Karla |
| B2B/B2G | Sin resultados financieros fabricados | Entrega de Azael |
| Informe | Arquitectura/limitaciones documentadas | Documento académico, protocolo y evidencias reales |
| Despliegue | Configuración y guía | Karla crea app con permiso admin |

La simulación no acredita tiempo liberado, empleo formal, convenio comunitario
ni impacto económico. No declarar finalizado el proyecto con esta migración.

## Validación local realizada

11 pruebas automatizadas: navegación de cinco pantallas con Streamlit AppTest,
ejecución del demo, 16 alcaldías y procedencia ENUT, rechazo por horario/tipo/
distancia/cupo, entradas inválidas, duplicados, confirmación transaccional,
reversión de doble confirmación y concurrencia sobre el último cupo en SQLite.
No se ejecutó Docker ni despliegue Cloud ni PostgreSQL remoto.
