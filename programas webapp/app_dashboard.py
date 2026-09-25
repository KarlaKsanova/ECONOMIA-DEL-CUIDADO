"""Dashboard accesible del Observatorio de la Economía del Cuidado.

Ejecutar con: ``streamlit run app_dashboard.py``.
"""

from __future__ import annotations

import html
import os
import re
import unicodedata
from datetime import time
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from branca.colormap import linear
from branca.element import MacroElement, Template
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from streamlit_javascript import st_javascript
from streamlit_folium import st_folium

from database_setup import Base, Oferente, Solicitud
from etl_pipeline import construir_dataset_consolidado
from modelo_matching import MotorMatching


RADIO_MATCHING_KM = 10.0
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(ROOT_DIR, "sistema_vinculacion.db")
FUENTE_ACADEMICA = (
    "Fuente: Elaboración propia del Observatorio del Cuidado CDMX con datos "
    "geográficos y censales (INEGI 2020), infraestructura de asistencia social "
    "y estimaciones de la Encuesta Nacional para el Sistema de Cuidados "
    "(ENUT 2024)."
)

st.set_page_config(
    layout="wide",
    page_title="Observatorio del Cuidado CDMX",
    page_icon="💜",
)

st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        html, body, [class*="css"] {
            color: #31333F;
        }
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(180deg, #F6F7FB 0%, #EEF2FF 100%);
            color: #31333F;
        }
        [data-testid="stHeader"] {
            background: transparent;
        }
        .block-container {
            padding-top: 2.5rem;
            padding-bottom: 3rem;
        }
        .hero-panel {
            background: linear-gradient(135deg, #5B21B6 0%, #7C3AED 45%, #A855F7 100%);
            color: #FFFFFF;
            border-radius: 24px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 18px 42px rgba(91, 33, 182, 0.25);
            margin: 0.25rem 0 1.25rem 0;
        }
        .hero-panel h2 {
            color: #FFFFFF !important;
            margin: 0 0 0.25rem 0;
            font-size: 1.35rem;
        }
        .hero-panel p {
            color: rgba(255, 255, 255, 0.92) !important;
            margin: 0.2rem 0 0 0;
            line-height: 1.45;
        }
        .section-kicker {
            display: inline-block;
            padding: 0.25rem 0.65rem;
            border-radius: 999px;
            background: rgba(124, 58, 237, 0.10);
            color: #5B21B6;
            font-weight: 700;
            font-size: 0.78rem;
            letter-spacing: 0.02em;
            margin-bottom: 0.5rem;
        }
        .section-card {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid rgba(91, 33, 182, 0.10);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            box-shadow: 0 10px 28px rgba(30, 41, 59, 0.06);
            margin: 0.25rem 0 1rem 0;
        }
        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] label,
        [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] {
            color: #31333F;
        }
        [data-testid="stAppViewContainer"] p {
            line-height: 1.5;
        }
        [data-testid="stMetric"] {
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFF 100%);
            border: 1px solid rgba(91, 33, 182, 0.12);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: 0 12px 28px rgba(30, 41, 59, 0.10);
            position: relative;
            overflow: hidden;
        }
        [data-testid="stMetric"]::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 4px;
            background: linear-gradient(180deg, #8B5CF6 0%, #EC4899 100%);
        }
        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"] {
            color: #31333F !important;
        }
        [data-baseweb="tab-list"] {
            background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(245,243,255,0.95));
            border-radius: 16px;
            padding: 0.35rem;
            border: 1px solid rgba(91, 33, 182, 0.10);
        }
        [data-baseweb="tab"] {
            color: #31333F !important;
            font-weight: 600;
        }
        [data-baseweb="tab"][aria-selected="true"] {
            color: #5B21B6 !important;
            background: rgba(91, 33, 182, 0.12);
            border-bottom-color: #5B21B6 !important;
        }
        [data-baseweb="tab"]:nth-child(1) {
            --tab-accent: #2563EB;
        }
        [data-baseweb="tab"]:nth-child(2) {
            --tab-accent: #DB2777;
        }
        [data-baseweb="tab"]:nth-child(3) {
            --tab-accent: #0F766E;
        }
        [data-baseweb="tab"]:hover {
            color: var(--tab-accent) !important;
            background: color-mix(in srgb, var(--tab-accent) 9%, white);
        }
        [data-baseweb="tab"][aria-selected="true"] {
            color: var(--tab-accent) !important;
            border-bottom-color: var(--tab-accent) !important;
        }
        .brand-mark {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            color: #5B21B6;
            font-size: 0.8rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.3rem;
        }
        .brand-mark span {
            display: inline-grid;
            place-items: center;
            width: 1.7rem;
            height: 1.7rem;
            border-radius: 0.6rem;
            background: linear-gradient(135deg, #7C3AED, #EC4899);
            color: #FFFFFF;
            box-shadow: 0 6px 14px rgba(124, 58, 237, 0.28);
        }
        .source-strip {
            background: #FFFBEB;
            border-left: 4px solid #F59E0B;
            border-radius: 10px;
            padding: 0.55rem 0.75rem;
        }
        .source-strip p {
            margin: 0;
            color: #713F12 !important;
            font-size: 0.82rem;
        }
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stTimeInput"] input,
        [data-testid="stSelectbox"] > div,
        [data-testid="stMultiSelect"] > div {
            background: #FFFFFF;
            color: #31333F;
        }
        [data-testid="stAlert"] {
            color: #31333F;
            border-radius: 14px;
        }
        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
        }
        @media (max-width: 768px) {
            .block-container {
                padding: 1rem 0.75rem 2rem;
            }
            [data-testid="stButton"] button {
                min-height: 3.4rem;
                width: 100%;
                border-radius: 14px;
                font-size: 1.05rem;
                font-weight: 700;
            }
            .mobile-step {
                border-left: 4px solid #8B5CF6;
                background: rgba(255, 255, 255, 0.86);
                border-radius: 0 14px 14px 0;
                padding: 0.8rem 0.9rem;
                margin: 0.6rem 0;
            }
            .mobile-kpi {
                margin: 0.45rem 0;
            }
            [data-testid="stAppViewContainer"] h1 {
                font-size: 1.65rem;
                line-height: 1.2;
            }
            [data-testid="stAppViewContainer"] h2 {
                font-size: 1.25rem;
                line-height: 1.25;
            }
            [data-testid="stAppViewContainer"] h3 {
                font-size: 1.05rem;
                line-height: 1.3;
            }
            [data-testid="stAppViewContainer"] p,
            [data-testid="stAppViewContainer"] label,
            [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] {
                font-size: 0.95rem;
            }
            [data-testid="stHorizontalBlock"] {
                flex-direction: column;
                gap: 0.6rem;
            }
            [data-testid="stMetric"] {
                min-width: 100%;
                padding: 0.8rem 0.9rem;
            }
            [data-testid="stMetricValue"] {
                font-size: 1.25rem;
            }
            [data-testid="stMetricLabel"] {
                font-size: 0.9rem;
            }
            [data-baseweb="tab-list"] {
                overflow-x: auto;
                white-space: nowrap;
            }
            [data-testid="stRadio"] > div {
                flex-direction: column;
                align-items: flex-start;
            }
            div[data-testid="stButton"] > button,
            button[kind="primary"],
            button[kind="secondary"] {
                width: 100%;
            }
            [data-testid="stSelectbox"],
            [data-testid="stMultiSelect"],
            [data-testid="stTextInput"],
            [data-testid="stNumberInput"],
            [data-testid="stTimeInput"] {
                width: 100%;
            }
            [data-testid="stCaptionContainer"] {
                font-size: 0.82rem;
                line-height: 1.35;
            }
            .hero-panel {
                padding: 1rem 1rem;
                border-radius: 20px;
            }
            .hero-panel h2 {
                font-size: 1.15rem;
            }
            .brand-mark {
                font-size: 0.72rem;
            }
            .source-strip {
                padding: 0.5rem 0.65rem;
            }
            iframe,
            .stHtmlFrame,
            .element-container iframe {
                max-width: 100%;
            }
            [data-testid="stDataFrame"] {
                font-size: 0.84rem;
            }
            section.main iframe {
                height: 390px !important;
            }
        }
        @media (min-width: 769px) {
            section.main iframe {
                height: 560px !important;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Cargando evidencia territorial...")
def cargar_evidencia():
    dataset = construir_dataset_consolidado()
    dataset = dataset.copy()
    dataset["poblacion_dependiente"] = _calcular_poblacion_dependiente(dataset)
    columnas_caci = {
        "poblacion_total_infantes_0_2",
        "matricula_caci_infantes",
        "cobertura_caci_0_2_pct",
    }
    faltantes = columnas_caci.difference(dataset.columns)
    if faltantes:
        raise ValueError(
            "El dataset consolidado no contiene columnas CACI requeridas: "
            + ", ".join(sorted(faltantes))
        )
    poblacion_infantes = pd.to_numeric(
        dataset["poblacion_total_infantes_0_2"], errors="coerce"
    ).fillna(0)
    matricula_caci = pd.to_numeric(
        dataset["matricula_caci_infantes"], errors="coerce"
    ).fillna(0)
    dataset["poblacion_cubierta"] = matricula_caci
    dataset["personas_afectadas"] = (
        poblacion_infantes - dataset["poblacion_cubierta"]
    ).clip(lower=0)
    return dataset


def _normalizar_columna(columna: object) -> str:
    texto = unicodedata.normalize("NFKD", str(columna))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", texto.lower())


def _calcular_poblacion_dependiente(dataset: pd.DataFrame) -> pd.Series:
    """Suma infancias de 0-14 y personas de 60+ del censo territorial."""

    columnas = {_normalizar_columna(columna): columna for columna in dataset.columns}
    prefijos = [
        "pobde0a4",
        "pobde5a9",
        "pobde10a14",
        "pobde60a64",
        "pobde65a69",
        "pobde70a74",
        "pobde75a79",
        "pobde80a84",
        "pob85",
    ]
    seleccionadas = {
        prefijo: next(
            (columna for normalizada, columna in columnas.items() if normalizada.startswith(prefijo)),
            None,
        )
        for prefijo in prefijos
    }
    faltantes = [prefijo for prefijo, columna in seleccionadas.items() if columna is None]
    if faltantes:
        raise ValueError(
            "No se pudieron identificar grupos de edad dependiente del censo: "
            + ", ".join(faltantes)
        )
    return dataset[[columna for columna in seleccionadas.values() if columna is not None]].apply(
        pd.to_numeric, errors="coerce"
    ).fillna(0).sum(axis=1)


def _formato_alcaldia(valor: str) -> str:
    return str(valor).title()


def _crear_mapa(dataset: pd.DataFrame, metrica: str) -> folium.Map:
    mapa_data = dataset.to_crs(epsg=4326).copy()
    min_longitud, min_latitud, max_longitud, max_latitud = mapa_data.total_bounds
    if not all(
        pd.notna(valor)
        for valor in (min_longitud, min_latitud, max_longitud, max_latitud)
    ):
        raise ValueError("El dataset no contiene límites geográficos válidos.")
    columna_metrica = {
        "Déficit de Infraestructura (Guarderías)": "personas_afectadas",
        "Abandono Laboral por Cuidados": "abandono_laboral_cuidados",
    }[metrica]
    valores = pd.to_numeric(mapa_data[columna_metrica], errors="coerce").fillna(0)
    minimo = float(valores.min())
    maximo = max(float(valores.max()), minimo + 1)
    escala = (
        linear.Purples_09.scale(minimo, maximo)
        if columna_metrica == "abandono_laboral_cuidados"
        else linear.Blues_09.scale(minimo, maximo)
    )
    escala.caption = metrica

    mapa = folium.Map(
        location=[
            (min_latitud + max_latitud) / 2,
            (min_longitud + max_longitud) / 2,
        ],
        zoom_start=10,
        max_bounds=True,
        tiles="OpenStreetMap",
        control_scale=True,
    )
    bounds = [[min_latitud, min_longitud], [max_latitud, max_longitud]]
    mapa.fit_bounds(bounds)
    bounds_js = Template(
        """
        {% macro script(this, kwargs) %}
        var bounds = L.latLngBounds({{ this.bounds|tojson }});
        {{ this._parent.get_name() }}.setMaxBounds(bounds);
        {{ this._parent.get_name() }}.fitBounds(bounds);
        {% endmacro %}
        """
    )
    bloque_bounds = MacroElement()
    bloque_bounds._template = bounds_js
    bloque_bounds.bounds = bounds
    mapa.add_child(bloque_bounds)
    for _, fila in mapa_data.iterrows():
        nombre = _formato_alcaldia(fila["alcaldia"])
        valor_metrica = pd.to_numeric(fila[columna_metrica], errors="coerce")
        valor_metrica = 0.0 if pd.isna(valor_metrica) else float(valor_metrica)
        text = (
            "<div style='max-width: 220px; white-space: normal; "
            "word-wrap: break-word;'>"
            f"<strong>Alcaldía:</strong> {html.escape(nombre)}<br>"
            f"<strong>Infantes sin cobertura CACI:</strong> "
            f"{fila['personas_afectadas']:,.0f}<br>"
            f"<strong>Cobertura CACI (0-2):</strong> "
            f"{fila['cobertura_caci_0_2_pct']:.1f}%<br>"
            f"<strong>Matrícula CACI:</strong> "
            f"{fila['matricula_caci_infantes']:,.0f}<br>"
            f"<strong>Guarderías:</strong> {fila['No_Guard']:,.0f}<br>"
            f"<strong>Abandono laboral:</strong> {fila['abandono_laboral_cuidados']:,.0f} "
            "personas dejaron su empleo para cuidar."
            "</div>"
        )
        folium.GeoJson(
            data=fila.geometry.__geo_interface__,
            style_function=lambda _, color=escala(valor_metrica): {
                "fillColor": color,
                "color": "#475569",
                "weight": 1.2,
                "fillOpacity": 0.86,
            },
            highlight_function=lambda _: {
                "weight": 3,
                "color": "#7c3aed",
                "fillOpacity": 0.95,
            },
        ).add_child(folium.Tooltip(text, sticky=True)).add_to(mapa)
    escala.add_to(mapa)
    return mapa


def _metricas_principales(
    dataset: pd.DataFrame, es_movil: bool = False
) -> None:
    total_guarderias = dataset["No_Guard"].sum()
    total_dependiente = dataset["poblacion_dependiente"].sum()
    total_afectadas = dataset["personas_afectadas"].sum()
    metricas = [
        ("Total de guarderías", f"{total_guarderias:,.0f}"),
        ("Población dependiente", f"{total_dependiente:,.0f} personas"),
        ("Infantes sin cobertura CACI", f"{total_afectadas:,.0f} personas"),
    ]
    if es_movil:
        for etiqueta, valor in metricas:
            st.metric(etiqueta, valor)
        return
    columnas = st.columns(3)
    for columna, (etiqueta, valor) in zip(columnas, metricas):
        columna.metric(etiqueta, valor)


def _extraer_porcentaje_macro(indicadores: dict[str, str], nombre: str) -> float:
    """Obtiene un porcentaje de los indicadores macro cargados por el ETL."""

    valor = indicadores.get(nombre)
    if valor is None:
        raise ValueError(f"Falta el indicador macro requerido: {nombre}")
    coincidencia = re.search(r"(\d+(?:[.,]\d+)?)\s*%", valor)
    if coincidencia is None:
        raise ValueError(f"El indicador macro no contiene un porcentaje: {nombre}")
    return float(coincidencia.group(1).replace(",", "."))


def _mostrar_contexto_enut(dataset: pd.DataFrame) -> None:
    indicadores = dataset.attrs["indicadores_pobreza_tiempo_cdmx"]
    indicadores_macro = dataset.attrs["indicadores_macro_economia_cuidado"]
    st.caption(
        "Nota: Los indicadores de la ENUT 2024 reflejan la realidad estructural "
        "del trabajo de cuidado a nivel metropolitano (CDMX)."
    )
    metricas = [
        (
            "Personas que realizan cuidado",
            f"{indicadores['enut_personas_que_cuidan']:,.0f}",
        ),
        ("Población que cuida", f"{indicadores['enut_porcentaje_que_cuida']:.1f}%"),
        (
            "Horas de cuidado semanales (Mujeres)",
            f"{indicadores['enut_horas_cuidado_mujeres']:.1f}",
        ),
        (
            "TNRH aportado por mujeres",
            f"{_extraer_porcentaje_macro(indicadores_macro, 'Porcentaje del TNRH aportado por mujeres'):.1f}%",
        ),
        (
            "TNRH en PIB CDMX",
            f"{_extraer_porcentaje_macro(indicadores_macro, 'Participación del TNRH en el PIB CDMX'):.1f}%",
        ),
    ]
    if st.session_state.get("es_movil", False):
        for etiqueta, valor in metricas:
            st.markdown('<div class="mobile-kpi">', unsafe_allow_html=True)
            st.metric(etiqueta, valor)
            st.markdown("</div>", unsafe_allow_html=True)
        return
    columnas = st.columns(len(metricas))
    for columna, (etiqueta, valor) in zip(columnas, metricas):
        columna.metric(etiqueta, valor)


def mostrar_visor_territorial(dataset, es_movil: bool = False) -> None:
    st.markdown('<div class="section-kicker">Lectura territorial</div>', unsafe_allow_html=True)
    st.header("Mapa del cuidado por alcaldía")
    st.markdown(
        '<div class="section-card">Consulta dónde falta más apoyo para el cuidado '
        "y cómo cambia el impacto cuando la oferta de guarderías es limitada."
        "</div>",
        unsafe_allow_html=True,
    )
    metrica = st.radio(
        "Métrica del mapa",
        [
            "Déficit de Infraestructura (Guarderías)",
            "Abandono Laboral por Cuidados",
        ],
        horizontal=not es_movil,
    )
    _mostrar_contexto_enut(dataset)
    mapa = _crear_mapa(dataset, metrica)
    _ = st_folium(mapa, use_container_width=True, height=390 if es_movil else 560)
    st.markdown(
        f'<div class="source-strip"><p>{FUENTE_ACADEMICA}</p></div>',
        unsafe_allow_html=True,
    )
    tabla = dataset[
        [
            "alcaldia",
            "poblacion_dependiente",
            "No_Guard",
            "cobertura_caci_0_2_pct",
            "matricula_caci_infantes",
            "personas_afectadas",
            "abandono_laboral_cuidados",
        ]
    ].copy()
    tabla["alcaldia"] = tabla["alcaldia"].map(_formato_alcaldia)
    tabla.columns = [
        "Alcaldía",
        "Población que requiere cuidado",
        "Guarderías disponibles",
        "Cobertura CACI (0-2)",
        "Matrícula CACI",
        "Personas afectadas sin acceso",
        "Abandono laboral por cuidados",
    ]
    formato_tabla = {
        "Población que requiere cuidado": "{:,.0f}",
        "Guarderías disponibles": "{:,.0f}",
        "Cobertura CACI (0-2)": "{:.1f}%",
        "Matrícula CACI": "{:,.0f}",
        "Personas afectadas sin acceso": "{:,.0f}",
        "Abandono laboral por cuidados": "{:,.0f}",
    }
    if es_movil:
        st.subheader("Resumen por alcaldía")
        for _, fila in tabla.iterrows():
            with st.expander(fila["Alcaldía"], expanded=False):
                st.metric(
                    "Personas afectadas sin acceso",
                    formato_tabla["Personas afectadas sin acceso"].format(
                        fila["Personas afectadas sin acceso"]
                    ),
                )
                st.write(
                    f"**Cobertura CACI:** {formato_tabla['Cobertura CACI (0-2)'].format(fila['Cobertura CACI (0-2)'])}"
                )
                st.write(
                    f"**Guarderías:** {formato_tabla['Guarderías disponibles'].format(fila['Guarderías disponibles'])}"
                )
                st.write(
                    f"**Abandono laboral:** {formato_tabla['Abandono laboral por cuidados'].format(fila['Abandono laboral por cuidados'])}"
                )
    else:
        st.dataframe(
            tabla.style.format(formato_tabla),
            use_container_width=True,
            hide_index=True,
        )
    st.subheader("Indicadores territoriales de oferta y demanda")
    indicadores_territoriales = dataset.set_index(
        dataset["alcaldia"].map(_formato_alcaldia)
    )[
        [
            "cobertura_caci_0_2_pct",
            "guarderias_por_1000_habitantes",
            "abandono_laboral_cuidados",
        ]
    ].rename(
        columns={
            "cobertura_caci_0_2_pct": "Cobertura CACI (%)",
            "guarderias_por_1000_habitantes": "Guarderías por 1,000 habitantes",
            "abandono_laboral_cuidados": "Abandono laboral por cuidados",
        }
    )
    if not es_movil:
        st.bar_chart(indicadores_territoriales)


def mostrar_comparativo_cuidado(
    dataset: pd.DataFrame, es_movil: bool = False
) -> None:
    """Presenta un comparativo territorial orientado a la toma de decisiones."""

    st.markdown(
        '<div class="section-kicker">Comparativo territorial</div>',
        unsafe_allow_html=True,
    )
    st.header("Brechas de cuidado por alcaldía")
    st.markdown(
        '<div class="section-card">Selecciona un indicador para ordenar las '
        "alcaldías y observa cómo se relacionan la oferta de servicios, la "
        "demanda de cuidado y sus efectos laborales.</div>",
        unsafe_allow_html=True,
    )

    columnas_requeridas = {
        "alcaldia",
        "cobertura_caci_0_2_pct",
        "guarderias_por_1000_habitantes",
        "personas_afectadas",
        "abandono_laboral_cuidados",
        "poblacion_dependiente",
        "No_Guard",
    }
    faltantes = columnas_requeridas.difference(dataset.columns)
    if faltantes:
        raise ValueError(
            "El comparativo territorial requiere columnas ausentes: "
            + ", ".join(sorted(faltantes))
        )

    indicadores = {
        "Personas afectadas sin acceso": {
            "columna": "personas_afectadas",
            "formato": "{:,.0f}",
            "descripcion": "Mayor valor = mayor cantidad estimada de infantes sin cobertura.",
        },
        "Abandono laboral por cuidados": {
            "columna": "abandono_laboral_cuidados",
            "formato": "{:,.0f}",
            "descripcion": "Mayor valor = mayor impacto laboral asociado al cuidado.",
        },
        "Cobertura CACI (0-2)": {
            "columna": "cobertura_caci_0_2_pct",
            "formato": "{:.1f}%",
            "descripcion": "Menor valor = menor cobertura de atención infantil.",
        },
        "Guarderías por 1,000 habitantes": {
            "columna": "guarderias_por_1000_habitantes",
            "formato": "{:.2f}",
            "descripcion": "Menor valor = menor disponibilidad relativa de guarderías.",
        },
    }
    indicador = st.selectbox(
        "Indicador para ordenar el ranking",
        list(indicadores),
        key="comparativo_indicador",
    )
    configuracion = indicadores[indicador]
    columna_indicador = configuracion["columna"]
    ranking_ascendente = indicador in {
        "Cobertura CACI (0-2)",
        "Guarderías por 1,000 habitantes",
    }

    comparativo = dataset[
        [
            "alcaldia",
            "poblacion_dependiente",
            "No_Guard",
            "cobertura_caci_0_2_pct",
            "guarderias_por_1000_habitantes",
            "personas_afectadas",
            "abandono_laboral_cuidados",
        ]
    ].copy()
    comparativo["alcaldia"] = comparativo["alcaldia"].map(_formato_alcaldia)
    comparativo[columna_indicador] = pd.to_numeric(
        comparativo[columna_indicador], errors="coerce"
    ).fillna(0)
    comparativo = comparativo.sort_values(
        columna_indicador,
        ascending=ranking_ascendente,
    ).reset_index(drop=True)
    comparativo.insert(0, "Posición", range(1, len(comparativo) + 1))

    zonas = sorted(comparativo["alcaldia"].tolist())
    zona = st.selectbox(
        "Alcaldía para el resumen ejecutivo",
        zonas,
        key="comparativo_alcaldia",
    )
    fila = comparativo.loc[comparativo["alcaldia"] == zona].iloc[0]
    posicion = int(
        comparativo.index[comparativo["alcaldia"] == zona][0] + 1
    )
    promedio = comparativo[columna_indicador].mean()
    valor = float(fila[columna_indicador])
    diferencia = valor - promedio
    direccion = "por encima" if diferencia >= 0 else "por debajo"

    metricas = [
        ("Indicador seleccionado", configuracion["formato"].format(valor)),
        ("Posición en el ranking", f"{posicion} de {len(comparativo)}"),
        ("Guarderías disponibles", f"{float(fila['No_Guard']):,.0f}"),
        ("Población dependiente", f"{float(fila['poblacion_dependiente']):,.0f}"),
    ]
    if es_movil:
        for etiqueta, valor_kpi in metricas:
            st.metric(etiqueta, valor_kpi)
    else:
        columnas = st.columns(len(metricas))
        for columna, (etiqueta, valor_kpi) in zip(columnas, metricas):
            columna.metric(etiqueta, valor_kpi)

    st.caption(
        f"{configuracion['descripcion']} La alcaldía seleccionada está "
        f"{abs(diferencia):,.2f} unidades {direccion} del promedio de la CDMX."
    )

    st.subheader(f"Resumen ejecutivo · {zona}")
    st.markdown(
        f'<div class="section-card"><strong>{zona}</strong> ocupa la posición '
        f"<strong>{posicion}</strong> del ranking de <strong>{indicador.lower()}"
        f"</strong>, con un valor de <strong>"
        f"{configuracion['formato'].format(valor)}</strong>. Registra "
        f"<strong>{float(fila['cobertura_caci_0_2_pct']):.1f}%</strong> de "
        f"cobertura CACI para población de 0 a 2 años, "
        f"<strong>{float(fila['personas_afectadas']):,.0f}</strong> personas "
        "afectadas sin acceso y "
        f"<strong>{float(fila['abandono_laboral_cuidados']):,.0f}</strong> "
        "casos estimados de abandono laboral por cuidados.</div>",
        unsafe_allow_html=True,
    )

    st.subheader("Ranking territorial")
    tabla = comparativo.rename(
        columns={
            "alcaldia": "Alcaldía",
            "poblacion_dependiente": "Población dependiente",
            "No_Guard": "Guarderías",
            "cobertura_caci_0_2_pct": "Cobertura CACI (%)",
            "guarderias_por_1000_habitantes": "Guarderías / 1,000 hab.",
            "personas_afectadas": "Personas afectadas",
            "abandono_laboral_cuidados": "Abandono laboral por cuidados",
        }
    )
    formato_comparativo = {
        "Población dependiente": "{:,.0f}",
        "Guarderías": "{:,.0f}",
        "Cobertura CACI (%)": "{:.1f}%",
        "Guarderías / 1,000 hab.": "{:.2f}",
        "Personas afectadas": "{:,.0f}",
        "Abandono laboral por cuidados": "{:,.0f}",
    }
    if es_movil:
        for _, fila_ranking in tabla.iterrows():
            with st.expander(
                f"{int(fila_ranking['Posición'])}. {fila_ranking['Alcaldía']}",
                expanded=False,
            ):
                st.write(
                    f"**{indicador}:** {configuracion['formato'].format(float(fila_ranking[columna_indicador]))}"
                )
                st.write(
                    f"**Cobertura CACI:** {formato_comparativo['Cobertura CACI (%)'].format(fila_ranking['Cobertura CACI (%)'])}"
                )
                st.write(
                    f"**Personas afectadas:** {formato_comparativo['Personas afectadas'].format(fila_ranking['Personas afectadas'])}"
                )
    else:
        st.dataframe(
            tabla.style.format(formato_comparativo).background_gradient(
                subset=list(formato_comparativo),
                cmap="Purples",
            ),
            use_container_width=True,
            hide_index=True,
        )
    st.markdown(
        f'<div class="source-strip"><p>{FUENTE_ACADEMICA}</p></div>',
        unsafe_allow_html=True,
    )


def seed_datos_simulacion(
    dataset: pd.DataFrame,
    alcaldia: str,
    ruta_db: str | Path = DATABASE_PATH,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Si hace falta, siembra el piloto con proporciones del Censo territorial."""

    ruta = os.fspath(ruta_db)
    if not os.path.isabs(ruta):
        ruta = os.path.join(ROOT_DIR, ruta)
    ruta = os.path.abspath(ruta)
    engine = create_engine(f"sqlite:///{ruta}")
    try:
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            solicitudes_existentes = session.scalar(
                select(Solicitud).where(Solicitud.alcaldia == alcaldia)
            )
            oferentes_existentes = session.scalar(
                select(Oferente).where(Oferente.alcaldia == alcaldia)
            )

            if solicitudes_existentes is None or oferentes_existentes is None:
                fila = dataset.loc[dataset["alcaldia"] == alcaldia]
                if fila.empty:
                    raise ValueError(f"No existe evidencia territorial para {alcaldia}.")
                fila = fila.iloc[0]
                dependientes = pd.to_numeric(
                    dataset["poblacion_dependiente"], errors="coerce"
                ).fillna(0)
                total_dependientes = dependientes.sum()
                promedio_dependientes = dependientes[dependientes > 0].mean()
                if total_dependientes <= 0 or promedio_dependientes <= 0:
                    raise ValueError(
                        "No se puede sembrar el simulador sin población dependiente positiva."
                    )

                poblacion_zona = float(fila["poblacion_dependiente"])
                solicitudes = max(
                    15, round(15 * poblacion_zona / promedio_dependientes)
                )
                afectados = max(float(fila["personas_afectadas"]), 0)
                cobertura = max(
                    0.05,
                    1 - min(afectados / max(poblacion_zona, 1), 0.95),
                )
                oferentes = max(1, round(solicitudes * cobertura))
                centroide = dataset.loc[
                    dataset["alcaldia"] == alcaldia
                ].to_crs(epsg=4326).geometry.iloc[0].centroid
                colonia = f"Zona piloto {alcaldia.title()}"
                if solicitudes_existentes is None:
                    session.add_all(
                        [
                            Solicitud(
                                alcaldia=alcaldia,
                                colonia=colonia,
                                latitud=float(centroide.y),
                                longitud=float(centroide.x),
                                horario_requerido_inicio=time(8),
                                horario_requerido_fin=time(12),
                                dias_requeridos="lun,mar",
                            )
                            for _ in range(solicitudes)
                        ]
                    )
                if oferentes_existentes is None:
                    session.add_all(
                        [
                            Oferente(
                                alcaldia=alcaldia,
                                colonia=colonia,
                                latitud=float(centroide.y),
                                longitud=float(centroide.x),
                                horario_ofrecido_inicio=time(8),
                                horario_ofrecido_fin=time(12),
                                dias_ofrecidos="lun,mar",
                            )
                            for _ in range(oferentes)
                        ]
                    )
                session.commit()

            solicitudes_rows = session.scalars(
                select(Solicitud).where(Solicitud.alcaldia == alcaldia)
            ).all()
            oferentes_rows = session.scalars(
                select(Oferente).where(Oferente.alcaldia == alcaldia)
            ).all()
            solicitudes_frame = pd.DataFrame(
                [
                    {
                        "solicitud_id": fila.solicitud_id,
                        "latitud": fila.latitud,
                        "longitud": fila.longitud,
                        "horario_requerido_inicio": fila.horario_requerido_inicio,
                        "horario_requerido_fin": fila.horario_requerido_fin,
                        "dias_requeridos": fila.dias_requeridos,
                    }
                    for fila in solicitudes_rows
                ]
            )
            oferentes_frame = pd.DataFrame(
                [
                    {
                        "oferente_id": fila.oferente_id,
                        "latitud": fila.latitud,
                        "longitud": fila.longitud,
                        "horario_ofrecido_inicio": fila.horario_ofrecido_inicio,
                        "horario_ofrecido_fin": fila.horario_ofrecido_fin,
                        "dias_ofrecidos": fila.dias_ofrecidos,
                    }
                    for fila in oferentes_rows
                ]
            )
            return solicitudes_frame, oferentes_frame
    finally:
        engine.dispose()


def mostrar_simulador(dataset: pd.DataFrame, es_movil: bool = False) -> None:
    st.markdown('<div class="section-kicker">Escenario de simulación</div>', unsafe_allow_html=True)
    st.header("Simulación de asignación de cuidados")
    st.markdown(
        '<div class="section-card">Esta simulación usa datos reales del proyecto '
        "para mostrar, de forma clara, qué pasa cuando muchas familias necesitan "
        "apoyo y la oferta no alcanza.</div>",
        unsafe_allow_html=True,
    )
    alcaldias = sorted(dataset["alcaldia"].dropna().unique())
    zona = st.selectbox(
        "Elige una zona para observar el piloto",
        alcaldias or ["IZTAPALAPA"],
        index=(alcaldias.index("IZTAPALAPA") if "IZTAPALAPA" in alcaldias else 0),
    )
    st.caption(
        f"Escenario construido para {zona.title()} con proporciones reales de "
        "población dependiente y déficit territorial observadas en las fuentes."
    )

    boton = st.button(
        "Iniciar simulación" if es_movil else "Ejecutar Simulación de Asignación",
        type="primary",
        use_container_width=True,
        key="simulador_ejecutar",
    )
    if es_movil:
        st.markdown(
            '<div class="mobile-step"><strong>Paso 1 · Zona</strong><br>'
            "Selecciona la alcaldía donde quieres observar el piloto.</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="mobile-step"><strong>Paso 2 · Simulación</strong><br>'
            "Pulsa el botón para estimar cuántas familias encuentran apoyo.</div>",
            unsafe_allow_html=True,
        )
    if boton:
        solicitudes_frame, oferentes_frame = seed_datos_simulacion(
            dataset, zona
        )
        resultado = MotorMatching(max_distance_km=RADIO_MATCHING_KM).emparejar(
            solicitudes_frame, oferentes_frame
        )
        familias = len(resultado)
        vinculadas = int((resultado["estado"] == "emparejada").sum())
        sin_cobertura = familias - vinculadas

        if es_movil:
            st.metric("Familias que piden apoyo", f"{familias:,}")
            st.metric("Familias vinculadas", f"{vinculadas:,}")
            st.metric("Familias sin cobertura", f"{sin_cobertura:,}")
        else:
            columnas = st.columns(3)
            columnas[0].metric("Familias que piden apoyo", f"{familias:,}")
            columnas[1].metric("Familias vinculadas", f"{vinculadas:,}")
            columnas[2].metric("Familias sin cobertura", f"{sin_cobertura:,}")

        if sin_cobertura:
            st.warning(
                f"{sin_cobertura} familias no pudieron recibir apoyo en esta "
                "simulación porque la oferta disponible no fue suficiente."
            )
        else:
            st.success("Todas las familias encontraron una cuidadora compatible.")

        st.info(
            "Transparencia del algoritmo: el motor prioriza cercanía y horarios; "
            f"sin embargo, por el déficit estructural de oferta, {sin_cobertura} "
            "familias no pudieron ser vinculadas. No se expuso información "
            "personal (Privacidad por Diseño - UCA 1)."
        )
    st.markdown(
        f'<div class="source-strip"><p>{FUENTE_ACADEMICA}</p></div>',
        unsafe_allow_html=True,
    )


def mostrar_transparencia() -> None:
    st.markdown('<div class="section-kicker">Transparencia y límites</div>', unsafe_allow_html=True)
    st.header("Cómo decide el motor de vinculación")
    st.markdown(
        '<div class="section-card">Aquí explicamos, con lenguaje claro, cómo se '
        "emparejan las solicitudes y las personas cuidadoras, y cuáles son los "
        "límites del sistema.</div>",
        unsafe_allow_html=True,
    )
    with st.expander("UCA 1 · Privacidad por diseño", expanded=False):
        st.markdown(
            "- `Solicitudes` y `Oferentes` usan identificadores internos "
            "seudonimizados.\n"
            "- No se almacenan nombres reales, teléfonos, correos ni género.\n"
            "- El simulador no persiste datos personales.\n"
            "- La capa operativa conserva únicamente ubicación y horarios "
            "necesarios para el matching."
        )
    with st.expander("UCA 5/6 · Transparencia, sesgos y límites", expanded=False):
        st.markdown(
            "- La compatibilidad exige coincidencia de días y de la ventana horaria.\n"
            f"- La búsqueda geográfica usa un radio máximo de {RADIO_MATCHING_KM:g} km.\n"
            "- La puntuación pondera 60% proximidad y 40% cobertura horaria.\n"
            "- La asignación es uno-a-uno porque el esquema no registra capacidad "
            "múltiple por oferente.\n"
            "- La distancia puede actuar como proxy socioeconómico y favorecer "
            "zonas con más oferta.\n"
            "- Al no existir género en el OLTP, no se puede auditar ese sesgo."
        )
        st.info(
            "La demanda no atendida se conserva con motivos explícitos como "
            "`demanda_supera_oferta_zona`, `sin_compatibilidad_horaria` o "
            "`ubicacion_ausente`; no se fuerzan emparejamientos incompatibles."
        )


def main() -> None:
    dataset = cargar_evidencia()
    ancho_pantalla = st_javascript("window.innerWidth")
    if not isinstance(ancho_pantalla, (int, float)):
        ancho_pantalla = 1024
    es_movil = ancho_pantalla < 768
    st.session_state["es_movil"] = es_movil
    st.markdown(
        f'<div class="source-strip"><p>Vista '
        f'{"móvil" if es_movil else "escritorio"} · '
        f'{int(ancho_pantalla)} px</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="brand-mark"><span>💜</span> Observatorio del Cuidado</div>',
        unsafe_allow_html=True,
    )
    st.title("Observatorio del Cuidado CDMX")
    st.caption(
        "Información territorial para decisiones de cuidado en la CDMX"
    )
    st.markdown(
        """
        <div class="hero-panel">
            <h2>Un observatorio visual para entender la crisis del cuidado</h2>
            <p>Explora el mapa por alcaldía, revisa las métricas más importantes y
            simula cómo se distribuye la demanda cuando la oferta de cuidados no
            alcanza. Todas las cifras provienen de fuentes reales del proyecto.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _metricas_principales(dataset, es_movil)
    st.markdown(
        f'<div class="source-strip"><p>{FUENTE_ACADEMICA}</p></div>',
        unsafe_allow_html=True,
    )
    visor, comparativo, simulador, transparencia = st.tabs(
        [
            " Visor Territorial",
            " Comparativo de Cuidado",
            " Simulador de Vinculación",
            " Transparencia",
        ]
    )
    with visor:
        mostrar_visor_territorial(dataset, es_movil)
    with comparativo:
        mostrar_comparativo_cuidado(dataset, es_movil)
    with simulador:
        mostrar_simulador(dataset, es_movil)
    with transparencia:
        mostrar_transparencia()


if __name__ == "__main__":
    main()
