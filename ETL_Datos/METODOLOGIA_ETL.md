# Metodología técnica del proceso ETL
## Observatorio de Datos para la Economía del Cuidado - CDMX

### 1. Objetivo

Preparar bases de datos demográficas, de movilidad y
de empresas sintéticas para apoyar el desarrollo de
un observatorio de datos orientado a la innovación social
en la Ciudad de México.

### 2. Fuentes de información

#### 2.1 CONAPO
- Institución: Consejo Nacional de Población.
- Fuente: Proyecciones municipales de población.
- Periodo procesado: 2021-2030.
- Cobertura: 16 alcaldías de la Ciudad de México.
- Resultado: 320 registros y 27 columnas.

#### 2.2 Movilidad GTFS
- Fuente: Conjunto de datos de transporte en formato GTFS.
- Archivos utilizados: agency.txt, routes.txt,
  trips.txt, stops.txt y stop_times.txt.
- Resultado: 22,532 relaciones ruta-parada.
- Rutas: 300.
- Paradas: 10,961.

#### 2.3 Empresas B2B2C
- Fuente territorial: Catálogo de códigos postales
  de Correos de México.
- Archivo: Codigos_Postales_CDMX.xls.
- Empresas generadas: 50.
- Cobertura: 16 alcaldías.
- Semilla aleatoria: 42.
- Naturaleza: datos completamente sintéticos.

### 3. Extracción

Se utilizan archivos originales en formatos CSV,
TXT y XLS, conservados en la carpeta
01_Datos originales.

El procesamiento se realiza mediante scripts Python,
utilizando pandas, numpy y xlrd.

### 4. Transformación

#### 4.1 Datos demográficos

Se seleccionan los registros correspondientes
a la Ciudad de México y al periodo 2021-2030.

Se conservan variables de población por sexo,
año, alcaldía y grupos de edad.

#### 4.2 Datos de movilidad

Se relacionan las rutas de transporte con los
viajes y las paradas mediante los identificadores
disponibles en los archivos GTFS.

Se obtiene una base de relaciones únicas
entre rutas y paradas.

#### 4.3 Empresas sintéticas

Se utiliza el catálogo de códigos postales
como referencia territorial.

Se generan 50 registros simulados con
identificadores únicos y variables relacionadas
con empleo y uso del transporte público.

La semilla 42 permite reproducir la generación
bajo las mismas condiciones.

### 5. Carga

Los archivos procesados se exportan a la carpeta
02_Datos_Procesados:

1. CONAPO_CDMX_PROCESADO_2021_2030.csv
2. MOVILIDAD_CDMX_RUTAS_PARADAS.csv
3. EMPRESAS_B2B2C_CDMX.csv

El ETL principal coordina los tres módulos.

Los CSV existentes se conservan sin sobrescritura.

### 6. Validación de calidad

Resultados de la prueba final:

| Base | Registros | Columnas | Nulos | Filas duplicadas |
|---|---:|---:|---:|---:|
| CONAPO | 320 | 27 | 0 | 0 |
| Movilidad | 22532 | 9 | 0 | 0 |
| Empresas B2B2C | 50 | 12 | 0 | 0 |

Estas verificaciones no sustituyen todos los
controles de integridad de claves o calidad semántica.

### 7. Reproducibilidad

Se ejecutó el ETL integrado desde cero en
un entorno aislado.

- Código de salida: 0.
- Duración observada: 1.27 segundos.
- Bases generadas: 3 de 3.

Los resultados regenerados fueron equivalentes
a las bases principales en dimensiones,
columnas y contenido.

La comparación permitió tolerancias numéricas
de 1e-10.

### 8. Integración territorial

CONAPO utiliza NOM_MUN como referencia
del nombre de la alcaldía.

Empresas B2B2C utiliza D_mnpio.

Movilidad utiliza las coordenadas stop_lat
y stop_lon, sin asignación directa de alcaldía.

La vinculación territorial de las paradas requiere
un cruce geoespacial con límites oficiales.

Los códigos postales deben manejarse como texto
para preservar los ceros iniciales.

### 9. Limitaciones

- Las proyecciones de CONAPO no son conteos
  observados de población.
- Los datos B2B2C son simulados y no representan
  empresas reales.
- Los recorridos GTFS pueden extenderse fuera
  de los límites de la Ciudad de México.
- El README documenta una ruta TR13 de SEMOVI
  sin correspondencia en el catálogo de agencias.
- La integración geoespacial por alcaldía
  todavía no se ha implementado.
- La equivalencia de los CSV no demuestra por sí
  sola la validez de todas las fuentes originales.

### 10. Conclusión

La fase ETL permitió integrar y validar tres
conjuntos de datos para el observatorio.

Las pruebas demostraron que los archivos pueden
regenerarse desde cero y obtener resultados
equivalentes a las bases principales.

La siguiente fase consistirá en integrar estos
resultados con otros indicadores del sistema
de cuidados y preparar su utilización
en la plataforma del observatorio.
