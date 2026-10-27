# Arquitectura del segundo avance

Una aplicación desplegada con módulos internos. No requiere servicios
independientes ni nuevas cuentas de nube para cada módulo.

| Capa | Ubicación | Regla |
|---|---|---|
| Interfaz | cuidado/ui | Solo presentación y estado de sesión |
| Servicios | cuidado/services | Coordinar datos y dominio |
| Dominio | cuidado/domain | Sin dependencia de Streamlit ni SQL |
| Persistencia | cuidado/database | Conexión central y transacciones |
| ETL | cuidado/pipelines | Ejecutar explícitamente al actualizar fuentes |

## Compatibilidad y datos anteriores

Se conserva modelo_matching.py como implementación histórica uno a uno;
la app nueva usa cuidado/domain/centros.py. No convertir registros de
personas oferentes en centros automáticamente.
El esquema v2 usa nombres nuevos y no borra tablas Solicitudes/Oferentes.
La inicialización es explícita: `python -m cuidado.database.inicializar`.
`create_all` solo crea tablas ausentes: no sustituye futuras migraciones SQL
versionadas. No se ha ejecutado contra una base de producción.

## Persistencia y privacidad

La demostración funciona sin base de datos. Sus IDs y ubicaciones son
sintéticos. El servicio de confirmación es interno, no tiene ruta pública.
Antes de usarlo con personas reales: roles y autorización, canal privado de
captura, protocolo de privacidad, retención/eliminación, auditoría,
verificación institucional y mecanismo de seguimiento/cancelación.
UUID no vuelve anónima una ubicación. No publicar coordenadas individuales.

La conexión común acepta SQLite local o PostgreSQL por DATABASE_URL.
Las pruebas locales de transacciones usan SQLite; PostgreSQL y la nube
requieren validación en el entorno elegido antes de operar con registros.
Las credenciales se pasan por entorno, nunca por Git.

## Capacidad y algoritmo

Cada servicio representa una franja semanal con cupos independientes.
No duplicar la misma plaza física en dos servicios. Una confirmación consume
un cupo para toda la ventana, sin reutilizarlo en subhorarios. La actualización
condicionada a cupo > 0 y la unicidad de solicitud evitan sobreasignación y
doble confirmación; la transacción revierte el decremento ante errores.
La oferta debe ser compatible y el centro estar verificado.

El algoritmo greedy asigna por orden de entrada y usa distancia haversiana
como referencia. No optimiza globalmente ni modela tiempos de transporte.
Faltan comparación experimental, análisis territorial y validación del piloto.

## Datos analíticos

GeoParquet público versionado más metadata JSON, generados desde las fuentes
originales. El ETL conserva 16 alcaldías y reporta nulos. Las fuentes tienen
años/poblaciones distintos; revisar comparabilidad antes de afirmar impacto.
El indicador exploratorio `estimacion_cuidadores_sin_trabajo_mercado` distribuye
el total CDMX por población dependiente. No mide causalidad ni abandono.
Las 12.16 horas provienen del resumen ENUT para mujeres cuidadoras; las cifras
macroeconómicas conservan sus propios orígenes.
