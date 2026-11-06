# Observatorio de Datos
## Economía del Cuidado - Ciudad de México

### 1. Objetivo
Preparar datos demográficos, de movilidad y de empresas
simuladas para apoyar el desarrollo de un observatorio
de datos orientado al diseño de programas de innovación
social en la Ciudad de México.

### 2. Fuentes de datos

**CONAPO**
- Fuente: Consejo Nacional de Población.
- Datos: Proyecciones municipales de población.
- Periodo seleccionado: 2021-2030.
- Cobertura: 16 alcaldías de la Ciudad de México.
- Registros procesados: 320.

**Movilidad GTFS**
- Fuente: Conjunto de datos de transporte en formato GTFS.
- Archivos: agency, routes, trips, stops y stop_times.
- Resultado: 22,532 relaciones únicas ruta-parada.
- Rutas representadas: 300.
- Paradas representadas: 10,961.

**Empresas B2B2C**
- Fuente territorial: Catálogo de códigos postales
  de Correos de México.
- Empresas: 50 registros sintéticos.
- Cobertura: 16 alcaldías.
- Semilla aleatoria: 42.
- Los registros no representan empresas reales.

### 3. Scripts principales

- etl_movilidad_conapo.py
  Procesa proyecciones demográficas, movilidad GTFS y coordina la generación de empresas B2B2C.

- mock_datos_empresas.py
  Genera datos sintéticos para pruebas del módulo B2B2C.

### 4. Archivos procesados

- CONAPO_CDMX_PROCESADO_2021_2030.csv
- MOVILIDAD_CDMX_RUTAS_PARADAS.csv
- EMPRESAS_B2B2C_CDMX.csv

### 5. Validaciones

- Revisión de valores faltantes.
- Verificación de identificadores duplicados.
- Comprobación de cobertura territorial.
- Validación de relaciones entre rutas y paradas.
- Comprobación de consistencia de datos sintéticos.

### 6. Consideraciones

- Los datos de empresas son exclusivamente simulados.
- Las proyecciones de CONAPO no son conteos observados.
- El conjunto GTFS incluye recorridos que pueden
  extenderse fuera de los límites de la CDMX.
- Se identificó una ruta TR13 con agencia SEMOVI
  sin correspondencia en el catálogo de agencias.
- Los scripts evitan sobrescribir los CSV existentes.


### 7. Requisitos técnicos

El proyecto utiliza Python 3 y las siguientes bibliotecas:

- pandas: procesamiento de datos.
- numpy: generación de datos sintéticos.
- xlrd: lectura de archivos Excel .xls.

Las dependencias se encuentran en requirements.txt.

### 8. Instalación

1. Instalar Python 3.
2. Abrir una terminal en la carpeta principal del proyecto.
3. Ejecutar:

    py -m pip install -r requirements.txt

### 9. Ejecución de scripts

Los scripts se encuentran en 03_Scripts_Python.

Para ejecutar el ETL integrado de CONAPO, movilidad y empresas B2B2C:

    py "03_Scripts_Python/etl_movilidad_conapo.py"

Para ejecutar el generador de empresas de manera independiente:

    py "03_Scripts_Python/mock_datos_empresas.py"

Cuando se ejecuta de manera independiente, el generador solicita la ruta del archivo original de códigos postales en formato .xls.

Al ejecutar el ETL integrado, el generador B2B2C se invoca automáticamente si el CSV de empresas todavía no existe.

Los archivos CSV procesados se almacenan en
02_Datos_Procesados.

### 10. Recomendaciones

- Conservar los archivos originales sin modificaciones.
- Revisar las rutas de entrada antes de ejecutar.
- Validar los resultados después de cada procesamiento.
- No utilizar las empresas sintéticas como datos reales.

### 11. Pruebas de integración y reproducibilidad

Se realizó una ejecución conjunta del ETL en un entorno
aislado, inicialmente sin archivos CSV procesados.

Resultados:
- CONAPO: 320 registros y 27 columnas.
- Movilidad GTFS: 22,532 registros y 9 columnas.
- Empresas B2B2C: 50 registros y 12 columnas.
- Valores faltantes: 0 en las tres bases.
- Filas completamente duplicadas: 0.
- Código de salida del ETL: 0.
- Tiempo observado de ejecución: 1.27 segundos.

Las tres bases regeneradas presentaron dimensiones,
columnas y datos equivalentes a los archivos principales.

La comparación numérica utilizó una tolerancia de
1e-10 para contemplar pequeñas diferencias de precisión.

La reproducibilidad se verificó con las mismas fuentes,
scripts y configuración del entorno de pruebas.

### 12. Integración territorial

- CONAPO identifica alcaldías mediante NOM_MUN.
- Empresas B2B2C identifica alcaldías mediante D_mnpio.
- Movilidad GTFS contiene coordenadas stop_lat y stop_lon.
- La asignación de paradas a alcaldías requiere un
  cruce geoespacial con límites territoriales oficiales.
- Los códigos postales deben tratarse como texto para
  conservar los ceros iniciales.

### Uso de esta versión compartida en GitHub

Esta carpeta contiene los scripts Python, la documentación
técnica y tres archivos CSV procesados.

Los CSV pueden consultarse directamente sin ejecutar
el proceso ETL.

Para regenerar los resultados desde cero, es necesario
incorporar los archivos originales correspondientes
en la carpeta `01_Datos originales`.

Los archivos originales no están incluidos en esta
primera publicación mientras se revisan sus condiciones
de redistribución.

Los scripts utilizan rutas relativas y deben conservar
la estructura de carpetas documentada.

Para instalar las dependencias desde ETL_Datos:

```bash
py -m pip install -r requirements.txt
```

Para ejecutar el ETL integrado, una vez incorporadas
las fuentes originales:

```bash
py "03_Scripts_Python/etl_movilidad_conapo.py"
```

Importante: el ETL conserva los CSV existentes.
Para regenerarlos es necesario trabajar en una copia
de prueba con la carpeta de salida vacía.

Los datos B2B2C son sintéticos y no representan
empresas reales.
