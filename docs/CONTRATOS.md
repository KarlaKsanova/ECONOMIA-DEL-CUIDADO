# Contratos propuestos de integración

Estos contratos se preparan para recepción del trabajo; no declaran que los
módulos estén entregados ni sustituyen el trabajo asignado.

## Karla

Puede seguir entregando `etl_movilidad_conapo.py` y `mock_datos_empresas.py`
en `programas webapp/`. Marlon incorporará adaptadores en pipelines/services,
sin exigir que Karla reorganice su código antes de entregarlo.

Movilidad/CONAPO: tabla con clave territorial, año, variable, valor, unidad,
fuente y fecha de consulta; geometrías con CRS declarado. No agregar por
alcaldía antes de conservar la granularidad necesaria para accesibilidad.
Distinguir proyección demográfica de observación. No eliminar nulos sin
reportar cantidad y sesgo potencial. Rechazar duplicados de la clave acordada.

Plantilla sintética: empleado_id sintético, cp como texto de cinco caracteres,
alcaldia, latitud, longitud, metodo_geocodificacion y es_simulado=true.
Validar pertenencia territorial, coordenadas y códigos sin correspondencia.
Un centroide de CP no es un domicilio ni un tiempo de traslado.

## Azael

`modulo_b2b_b2g.py`: funciones importables, sin Streamlit ni lecturas de archivos
al importar. Entradas explícitas con unidades y año. Salida propuesta:
resultado, unidad, periodo, supuestos, fuentes y version_metodologia.
Validar números finitos y rangos; no convertir datos ausentes en ahorros cero.
Separar ahorro bruto, costo de intervención y beneficio neto; distinguir
recaudación tributaria y contribuciones de seguridad social.
No incorporar tasas legales/financieras sin fuente, fecha y ámbito aplicable.

## Aceptación común

Ejemplo mínimo reproducible, dependencias adicionales, contrato real de cada
función, fuentes y limitaciones. Ejecutar las pruebas de integración antes de
cambiar el registro de estado en cuidado/services/integraciones.py.
