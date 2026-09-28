

#  Contexto del Proyecto: Observatorio de la Economía del Cuidado CDMX y Sistema de Vinculación

## 1. Objetivo General y Eje Metodológico

Desarrollar un sistema integral en Python que incluya un Dashboard interactivo y un modelo de datos analítico. El objetivo es analizar el impacto de las responsabilidades de cuidado en la inserción laboral femenina en la CDMX y proponer un sistema de vinculación (matching) basado en zonas geográficas.

El proyecto sigue rigurosamente la secuencia transversal metodológica establecida por la UNRC:
`DATOS -> EVIDENCIA -> DECISIÓN -> PROGRAMA DE INNOVACIÓN SOCIAL`

## 2. Magnitud del Problema y Brechas Estructurales

La economía del cuidado comprende todas las actividades orientadas a satisfacer necesidades humanas esenciales (crianza, atención a personas mayores y con discapacidad). Su impacto en México se traduce en cifras críticas:

* **Magnitud Económica:** Equivale a más del 20% del PIB nacional (Cuenta Satélite del INEGI).


* **Carga de Género:** 75% del total de horas de cuidado no remunerado recaen sobre mujeres.


* **Población Afectada:** 40 millones de personas requieren cuidados, sostenidos por 6.5 millones de cuidadoras primarias que enfrentan "pobreza de tiempo".



El análisis de datos geoespaciales buscará visibilizar **4 Brechas Centrales**:

1. **Brecha Geográfica:** Concentración urbana vs. déficit rural.


2. **Brecha Generacional:** Demanda creciente por envejecimiento vs. oferta pública insuficiente.


3. **Brecha de Género:** Carga femenina sin compensación.


4. **Brecha de Formalidad:** 80% del sector operando en la informalidad.



## 3. Stack Tecnológico Requerido

* **Lenguaje:** Python 3.10+
* **Manipulación de datos:** pandas, numpy
* **Base de Datos:** PostgreSQL / SQLite (Diseño OLTP y OLAP)
* **Datos geoespaciales:** geopandas, shapely
* **Visualización y Dashboard:** streamlit, plotly, matplotlib, folium (mapas interactivos)
* **Algoritmos y Modelado:** scikit-learn

## 4. Archivos de Datos (Fuentes e Integración)

El ecosistema integra diversas fuentes (INEGI, DENUE, etc.) para el análisis demográfico, económico y geoespacial:

1. `ENUT_2024_CDMX_resumen_ponderado.csv`: Datos de pobreza de tiempo y horas de cuidado no remunerado.
2. `base_censo_CDMX_observatorio_v1.csv`: Población dependiente (adultos mayores, infantes) por Alcaldía.
3. `Equipamiento_de_asistencia_social.shp` (junto con `.dbf`, `.prj`, `.shx`): Archivo vectorial espacial (EPSG:32614). Contiene geometrías de polígonos, infraestructura de asistencia social instalada (ej. `No_Guard`) y demografía territorial, clasificado por `alcaldia` y `cve_col`.
4. `datos_observatorio_cuidado_alcaldias_cdmx.csv`: Base estructurada con 16 filas (alcaldías) y 15 columnas con variables censales, laborales e infraestructura.
5. `indicadores_macro_economia_cuidado.csv`: Tabla de datos macroeconómicos nacionales y capitalinos del TNRH.

**Nota Crítica de Integración GIS:** El pipeline ETL deberá cruzar las bases tabulares (CSVs) con el Shapefile (`.shp`) utilizando la variable territorial `alcaldia` mediante `geopandas`, mapeando la oferta de servicios frente a la demanda y la pobreza de tiempo.

## 5. Reglas de Negocio e Incidentes Críticos (UCA)

### 5.1. Leyes para la Protección de Datos (Privacidad Crítica)

* **Privacy by Design:** Obligación legal de proteger la privacidad de titulares vulnerables.
* Los datos sensibles del modelo de matching deben estar **seudonimizados** (aplicación de hashes SHA-256 o UUID a nombres o identificadores directos).
* **Arquitectura de 3 capas:** Ingesta (cifrada), Operativa/Matching (seudonimizada) y Analítica (Dashboard público con anonimización irreversible).

### 5.2. Práctica Profesional I y Fases del Piloto

* **Matching Delimitado:** El algoritmo de vinculación no procesará a toda la población. Se delimita estrictamente a un piloto en el Centro Comunitario 'Manos que Cuidan' (Iztapalapa), limitando el procesamiento a 15 familias solicitantes y 6 personas cuidadoras en 2 colonias.
* **Escalabilidad del Observatorio (Plataforma):** Tras la fase local, la visualización de datos se escalará a 3 estados prioritarios (CDMX, Edomex, Jalisco) antes de su fase nacional.



### 5.3. Inteligencia de Negocios

El dashboard superará la medición exclusiva de crecimiento económico. El mapa de KPIs priorizará indicadores de cobertura social, necesidades no atendidas y brechas territoriales, evidenciando estadísticamente cómo el trabajo no remunerado deprime la Población Económicamente Activa (PEA) femenina.

### 5.4. Analítica para los Negocios (Creación de Valor Compartido)

El proyecto se fundamenta en el concepto de **Valor Compartido** (Porter & Kramer). Las soluciones propuestas (ej. guarderías corporativas, políticas de conciliación) demostrarán a través de los datos que la rentabilidad empresarial (reducción del 30% del ausentismo, retención de talento) y el bienestar social son interdependientes.

### 5.5. Transparencia Algorítmica y Ética (Seminario de Titulación I)

El modelo de clasificación/matching con *scikit-learn* mitigará sesgos territoriales y de género. Bajo estrictos criterios científicos y éticos, cualquier falla, sesgo o baja participación algorítmica no será ocultada, sino que será documentada con precisión académica para los entregables de titulación.

## 6. Plan de Acción y Fases de Implementación Técnica

1. **Fase de Diseño y Arquitectura (Mes 1-4):** Diseño de la Base de Datos SQL (OLTP para transacciones de matching y OLAP para el Dashboard analítico).


2. **Fase de Integración de Datos (Mes 5-9):** Generación de Pipelines ETL para limpiar, cruzar y unificar los 5 archivos fuente tabulares con el archivo vectorial (Shapefile).


3. **Fase Piloto de Matching y Visualización (Mes 10-15):** Codificación del motor predictivo con *scikit-learn* (delimitado a Iztapalapa) y construcción del Dashboard interactivo multicapa (Streamlit + GeoPandas).


4. **Fase de Escala y Presentación (Mes 16+):** Despliegue en la nube (Google Cloud Run), monitoreo de estabilidad y entrega del documento de investigación con evidencias del impacto generado.