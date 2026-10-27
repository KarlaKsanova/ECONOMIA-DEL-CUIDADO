from __future__ import annotations
import html
import re
import unicodedata
import folium
import pandas as pd
import streamlit as st
from branca.colormap import linear
from branca.element import MacroElement, Template
from streamlit_folium import st_folium
from cuidado.services.evidencia import cargar_evidencia
FUENTE_ACADEMICA = "Fuentes: CSV y cartografía del repositorio. Años y alcances distintos; ver notas metodológicas."
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
        "Estimación territorial: cuidado sin trabajo de mercado": "estimacion_cuidadores_sin_trabajo_mercado",
    }[metrica]
    valores = pd.to_numeric(mapa_data[columna_metrica], errors="coerce").fillna(0)
    minimo = float(valores.min())
    maximo = max(float(valores.max()), minimo + 1)
    escala = (
        linear.Purples_09.scale(minimo, maximo)
        if columna_metrica == "estimacion_cuidadores_sin_trabajo_mercado"
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
            f"<strong>Estimación territorial:</strong> {fila['estimacion_cuidadores_sin_trabajo_mercado']:,.0f} "
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
        "del trabajo de cuidado a nivel de entidad (CDMX)."
    )
    metricas = [
        (
            "Personas que realizan cuidado",
            f"{indicadores['enut_personas_que_cuidan']:,.0f}",
        ),
        ("Población que cuida", f"{indicadores['enut_porcentaje_que_cuida']:.1f}%"),
        (
            "Horas semanales entre mujeres cuidadoras (ENUT)",
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
            "Estimación territorial: cuidado sin trabajo de mercado",
        ],
        horizontal=not es_movil,
    )
    _mostrar_contexto_enut(dataset)
    st.markdown(
        """
        <div class="structural-gaps">
            <div class="section-kicker">Eje central del análisis</div>
            <h2>Las 4 Brechas Estructurales del cuidado</h2>
            <p class="structural-gaps-intro">
                El mapa permite observar cómo estas desigualdades se expresan
                territorialmente en la Ciudad de México.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    brechas = [
        (
            "🌍",
            "Brecha Geográfica",
            "Concentración urbana vs. déficit rural.",
            "#2563EB",
        ),
        (
            "👵",
            "Brecha Generacional",
            "Demanda por envejecimiento vs. oferta pública.",
            "#7C3AED",
        ),
        (
            "👩",
            "Brecha de Género",
            "<strong>75%</strong> de la carga recae en mujeres sin compensación.",
            "#DB2777",
        ),
        (
            "🏢",
            "Brecha de Formalidad",
            "<strong>80%</strong> del sector opera en la informalidad.",
            "#0F766E",
        ),
    ]
    columnas_brechas = st.columns(4)
    for columna, (icono, titulo, descripcion, acento) in zip(
        columnas_brechas, brechas
    ):
        columna.markdown(
            f"""
            <div class="structural-gap-card" style="--gap-accent: {acento};">
                <div class="structural-gap-icon" role="img" aria-label="{titulo}">
                    {icono}
                </div>
                <h3>{titulo}</h3>
                <p>{descripcion}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
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
            "estimacion_cuidadores_sin_trabajo_mercado",
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
        "Estimación: cuidado sin trabajo de mercado",
    ]
    formato_tabla = {
        "Población que requiere cuidado": "{:,.0f}",
        "Guarderías disponibles": "{:,.0f}",
        "Cobertura CACI (0-2)": "{:.1f}%",
        "Matrícula CACI": "{:,.0f}",
        "Personas afectadas sin acceso": "{:,.0f}",
        "Estimación: cuidado sin trabajo de mercado": "{:,.0f}",
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
                    f"**Estimación territorial:** {formato_tabla['Estimación: cuidado sin trabajo de mercado'].format(fila['Estimación: cuidado sin trabajo de mercado'])}"
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
            "estimacion_cuidadores_sin_trabajo_mercado",
        ]
    ].rename(
        columns={
            "cobertura_caci_0_2_pct": "Cobertura CACI (%)",
            "guarderias_por_1000_habitantes": "Guarderías por 1,000 habitantes",
            "estimacion_cuidadores_sin_trabajo_mercado": "Estimación: cuidado sin trabajo de mercado",
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
        "estimacion_cuidadores_sin_trabajo_mercado",
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
        "Estimación: cuidado sin trabajo de mercado": {
            "columna": "estimacion_cuidadores_sin_trabajo_mercado",
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
            "estimacion_cuidadores_sin_trabajo_mercado",
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
        f"<strong>{float(fila['estimacion_cuidadores_sin_trabajo_mercado']):,.0f}</strong> "
        "personas estimadas que cuidan sin trabajo de mercado; distribución proporcional, no observación local.</div>",
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
            "estimacion_cuidadores_sin_trabajo_mercado": "Estimación: cuidado sin trabajo de mercado",
        }
    )
    formato_comparativo = {
        "Población dependiente": "{:,.0f}",
        "Guarderías": "{:,.0f}",
        "Cobertura CACI (%)": "{:.1f}%",
        "Guarderías / 1,000 hab.": "{:.2f}",
        "Personas afectadas": "{:,.0f}",
        "Estimación: cuidado sin trabajo de mercado": "{:,.0f}",
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
