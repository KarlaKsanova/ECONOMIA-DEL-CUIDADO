# Contexto del Proyecto: Observatorio de la Economía del Cuidado CDMX y Sistema de Vinculación B2B2C

## 1. Visión Estratégica y Eje Metodológico

El proyecto se aleja de los modelos de plataformas transaccionales de intermediación privada (los cuales tienden a perpetuar la informalidad laboral) para consolidarse como un Sistema B2B2C de Innovación Social y Valor Compartido. Desarrollar este sistema integral en Python incluye un Dashboard interactivo y un modelo de datos analítico que resuelve la falta de inserción laboral femenina operando en dos frentes:

* Solución Micro (Comunitaria - B2C): Un motor predictivo que vincula a familias con pobreza de tiempo con centros de cuidado comunitario consolidados. Esto libera el tiempo de las mujeres de forma segura, permitiendo su inserción al mercado laboral formal, y profesionaliza a las cuidadoras.
* Solución Macro (Corporativa y Gubernamental - B2B/B2G): Simuladores interactivos que demuestran con datos georreferenciados que financiar esta infraestructura de cuidados no es un gasto, sino una inversión con alto retorno.

El proyecto sigue rigurosamente la secuencia transversal metodológica establecida por la UNRC:
DATOS -> EVIDENCIA -> DECISIÓN -> PROGRAMA DE INNOVACIÓN SOCIAL

## 2. Magnitud del Problema y Brechas Estructurales

La economía del cuidado comprende todas las actividades orientadas a satisfacer necesidades humanas esenciales. Su impacto en México se traduce en cifras críticas:

* Magnitud Económica: Equivale a más del 20% del PIB nacional (Cuenta Satélite del INEGI).
* Carga de Género: 75% del total de horas de cuidado no remunerado recaen sobre mujeres.
* Población Afectada: 40 millones de personas requieren cuidados, sostenidos por 6.5 millones de cuidadoras primarias que enfrentan "pobreza de tiempo".

El análisis de datos geoespaciales buscará visibilizar 4 Brechas Centrales:

1. Brecha Geográfica: Concentración urbana vs. déficit rural.
2. Brecha Generacional: Demanda creciente por envejecimiento vs. oferta pública insuficiente.
3. Brecha de Género: Carga femenina sin compensación.
4. Brecha de Formalidad: 80% del sector operando en la informalidad.

## 3. Ecosistema de Módulos (La Plataforma Web)

Para ejecutar la solución de política pública y negocios, el Dashboard integra los siguientes módulos funcionales:

* Motor de Matching (Prueba de Concepto en Iztapalapa con escalabilidad a CDMX): Algoritmo de clasificación que vincula la oferta y demanda de cuidados en un radio delimitado, diseñado para expandirse a toda la ciudad.
* Auditoría de RRHH (Módulo B2B): Interfaz donde una empresa cruza los Códigos Postales de su plantilla laboral con el mapa de "desiertos de cuidado" para calcular su "Índice de Riesgo de Rotación".
* Calculadora de Retorno Fiscal (Módulo B2G): Simulador que proyecta la recaudación extra (ISR/IMSS) generada al liberar a mujeres PNEA hacia empleos formales mediante nuevas guarderías.
* Análisis de Movilidad (Isócronas): Integración del tiempo de traslado (radios de 30 minutos en transporte público) como variable crítica.
* Simulador Demográfico Predictivo: Proyección de demanda de cuidados hacia el año 2030 utilizando proyecciones poblacionales.

## 4. Stack Tecnológico y Arquitectura de Software

Para garantizar la escalabilidad y el control de versiones en el repositorio, la arquitectura se divide en componentes funcionales preparados para un despliegue a gran escala:

* Lenguaje: Python 3.10+
* Manipulación de datos: pandas, numpy
* Base de Datos: PostgreSQL / SQLite (Diseño OLTP y OLAP)
* Datos geoespaciales: geopandas, shapely
* Visualización y Dashboard: streamlit, plotly, matplotlib, folium
* Algoritmos y Modelado: scikit-learn

Distribución Base de Archivos:

* app_dashboard.py: Orquestador visual y UI de Streamlit. No procesa datos pesados, únicamente renderiza componentes y métricas.
* modelo_matching.py: Entrenamiento, predicción y seudonimización de datos. Inicia como piloto en Iztapalapa, pero el algoritmo es agnóstico (basado en coordenadas y tiempo, no en colonias fijas) para escalar automáticamente a toda la CDMX.
* etl_pipeline.py: Pipelines de extracción, transformación y carga (ETL), limpieza de nulos y cruces espaciales. Diseñado como un "ETL Universal" que procesa y unifica datos de las 16 alcaldías desde el día uno.
* database_setup.py: Configuración, esquemas y conexión de la base de datos SQL.
* Dockerfile: Instrucciones de contenedorización y configuración del entorno para el despliegue automatizado y escalable en Google Cloud Run.

## 5. Archivos de Datos (Fuentes e Integración)

El ecosistema integra diversas fuentes para el análisis demográfico, económico y geoespacial. El pipeline ETL debe mantener la lectura de los siguientes archivos locales a nivel ciudad:

1. ENUT_2024_CDMX_resumen_ponderado.csv: Datos de pobreza de tiempo y horas de cuidado no remunerado.
2. base_censo_CDMX_observatorio_v1.csv: Población dependiente (adultos mayores, infantes) por Alcaldía.
3. Equipamiento_de_asistencia_social.shp (junto con .dbf, .prj, .shx): Archivo vectorial espacial (EPSG:32614). Contiene infraestructura de asistencia social instalada (ej. No_Guard) y demografía territorial.
4. datos_observatorio_cuidado_alcaldias_cdmx.csv: Base estructurada con 16 filas y 15 columnas con variables censales.
5. indicadores_macro_economia_cuidado.csv: Tabla de datos macroeconómicos del TNRH.
6. (Nuevas fuentes en recolección): Proyecciones CONAPO al 2030, coordenadas de transporte público (Metro/Cablebús) y CSV anonimizado con 50 CPs simulados para la prueba del módulo B2B.

Nota Crítica de Integración GIS: El pipeline en etl_pipeline.py deberá cruzar las bases tabulares (CSVs) con el Shapefile (.shp) utilizando la variable territorial "alcaldia" mediante geopandas, mapeando la oferta de servicios frente a la demanda y la pobreza de tiempo en toda la capital.

## 6. Reglas de Negocio e Incidentes Críticos (UCA)

### 6.1. Leyes para la Protección de Datos (Privacidad Crítica)

* Privacy by Design: Obligación legal de proteger la privacidad de titulares vulnerables.
* Los datos sensibles del modelo de matching deben estar seudonimizados (aplicación de hashes SHA-256 o UUID a nombres o identificadores directos).
* Arquitectura de 3 capas: Ingesta (cifrada), Operativa/Matching (seudonimizada) y Analítica (Dashboard público con anonimización irreversible).

### 6.2. Práctica Profesional I y Fases de Implementación

* Prueba de Concepto (PoC) en Iztapalapa: El algoritmo de vinculación iniciará de forma controlada. Se delimita estrictamente a un piloto en el Centro Comunitario 'Manos que Cuidan' (Iztapalapa), limitando el procesamiento inicial a 15 familias solicitantes y 6 personas cuidadoras en 2 colonias.
* Escalabilidad y Plan Final (Nivel CDMX): Aunque la validación inicial se realiza en Iztapalapa, toda la infraestructura técnica (ETL, variables de scikit-learn, simuladores B2B/B2G) está construida para operar con datos macro. Al validar el piloto, el sistema aplicará automáticamente el procesamiento a las 16 alcaldías de la CDMX, con una fase de expansión posterior a 3 estados prioritarios (CDMX, Edomex, Jalisco).

### 6.3. Inteligencia de Negocios

El dashboard superará la medición exclusiva de crecimiento económico. El mapa de KPIs priorizará indicadores de cobertura social, necesidades no atendidas y brechas territoriales, evidenciando estadísticamente cómo el trabajo no remunerado deprime la Población Económicamente Activa (PEA) femenina en la capital.

### 6.4. Analítica para los Negocios (Creación de Valor Compartido)

El proyecto se fundamenta en el concepto de Valor Compartido (Porter & Kramer). Las soluciones propuestas (ej. guarderías corporativas, políticas de conciliación) demostrarán a través de los datos que la rentabilidad empresarial (reducción del 30% del ausentismo, retención de talento) y el bienestar social son interdependientes en un entorno urbano complejo.

### 6.5. Transparencia Algorítmica y Ética (Seminario de Titulación I)

El modelo de clasificación/matching con scikit-learn mitigará sesgos territoriales y de género. Bajo estrictos criterios científicos y éticos, cualquier falla, sesgo o baja participación algorítmica no será ocultada, sino que será documentada con precisión académica para los entregables de titulación.

## 7. Plan de Acción y Fases de Implementación Técnica

1. Fase de Diseño y Arquitectura : Diseño de la Base de Datos SQL (OLTP para transacciones de matching y OLAP para el Dashboard analítico) y definición de la arquitectura base del código universal.
2. Fase de Integración de Datos : Generación de Pipelines ETL para limpiar, cruzar y unificar los archivos fuente tabulares con el archivo vectorial (Shapefile) de toda la ciudad.
3. Fase Piloto de Matching y Visualización : Codificación del motor predictivo con scikit-learn (fase inicial delimitada a Iztapalapa) y construcción del Dashboard interactivo multicapa.
4. Fase de Escala CDMX y Presentación : Retiro de filtros locales para el procesamiento de toda la Ciudad de México, despliegue en la nube (Google Cloud Run), monitoreo de estabilidad y entrega del documento de investigación con evidencias del impacto generado a nivel urbano.