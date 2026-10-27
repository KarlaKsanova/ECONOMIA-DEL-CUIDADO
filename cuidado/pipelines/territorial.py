"""ETL territorial para el Observatorio de la Economía del Cuidado.

El resultado conserva una fila por alcaldía de la CDMX. La infraestructura
del Shapefile se agrega antes de unirla con las fuentes tabulares para evitar
duplicar los indicadores territoriales por cada colonia o polígono.
"""

from __future__ import annotations

import os
import re
import unicodedata
from pathlib import Path
from typing import Iterable

import geopandas as gpd
import pandas as pd


ROOT_DIR = str(Path(__file__).resolve().parents[2])
DEFAULT_OBSERVATORIO = os.path.join(
    ROOT_DIR, "data", "raw", "datos_observatorio_cuidado_alcaldias_cdmx.csv"
)
DEFAULT_CENSO = os.path.join(
    ROOT_DIR, "data", "raw", "base_censo_CDMX_observatorio_v1.csv"
)
DEFAULT_ENUT = os.path.join(
    ROOT_DIR, "data", "raw", "ENUT_2024_CDMX_resumen_ponderado.csv"
)
DEFAULT_MACRO = os.path.join(
    ROOT_DIR, "data", "raw", "indicadores_macro_economia_cuidado.csv"
)
DEFAULT_SHAPEFILE = os.path.join(
    ROOT_DIR, "visualizacion", "Equipamiento_de_asistencia_social.shp"
)


def _normalizar_alcaldia(valor: object) -> str | None:
    """Devuelve una llave comparable para nombres de alcaldías."""

    if pd.isna(valor):
        return None
    texto = str(valor).strip().upper().replace("&", " Y ")
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    texto = re.sub(r"[^A-Z0-9]+", " ", texto).strip()
    aliases = {
        "ALVARO OBREGON": "ALVARO OBREGON",
        "LVARO OBREGON": "ALVARO OBREGON",
        "BENITO JU REZ": "BENITO JUAREZ",
        "BENITO JUAREZ": "BENITO JUAREZ",
        "COYOAC N": "COYOACAN",
        "COYOACAN": "COYOACAN",
        "CUAUHT MOC": "CUAUHTEMOC",
        "CUAUHTEMOC": "CUAUHTEMOC",
        "TLAHUAC": "TLAHUAC",
    }
    return aliases.get(texto, texto)


def _limpiar_tabla(tabla: pd.DataFrame) -> pd.DataFrame:
    """Normaliza encabezados y elimina filas completamente vacías."""

    limpia = tabla.copy()
    limpia.columns = [
        str(columna).replace("\ufeff", "").strip() for columna in limpia.columns
    ]
    limpia = limpia.dropna(how="all").reset_index(drop=True)
    if "alcaldia" in limpia.columns:
        limpia["alcaldia"] = limpia["alcaldia"].map(_normalizar_alcaldia)
    return limpia


def cargar_tabulares(
    rutas: Iterable[str | Path],
    *,
    encoding: str = "utf-8-sig",
) -> dict[str, pd.DataFrame]:
    """Carga y limpia archivos CSV tabulares indexados por nombre de archivo."""

    tablas: dict[str, pd.DataFrame] = {}
    for ruta in rutas:
        path = Path(ruta)
        if not path.is_file():
            raise FileNotFoundError(f"No existe el archivo tabular: {path}")
        tablas[path.stem] = _limpiar_tabla(pd.read_csv(path, encoding=encoding))
    return tablas


def cargar_shapefile(ruta: str | Path = DEFAULT_SHAPEFILE) -> gpd.GeoDataFrame:
    """Carga el Shapefile y valida sus columnas geográficas esenciales."""

    path = Path(ruta)
    if not path.is_file():
        raise FileNotFoundError(f"No existe el Shapefile: {path}")
    mapa = gpd.read_file(path)
    requeridas = {"alcaldia", "geometry"}
    faltantes = requeridas.difference(mapa.columns)
    if faltantes:
        raise ValueError(
            f"El Shapefile no contiene las columnas requeridas: {sorted(faltantes)}"
        )
    mapa = mapa.loc[mapa.geometry.notna() & ~mapa.geometry.is_empty].copy()
    mapa["alcaldia"] = mapa["alcaldia"].map(_normalizar_alcaldia)
    return mapa


def _agregar_infraestructura(mapa: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Disuelve polígonos por alcaldía y suma sus atributos de infraestructura."""

    mapa = mapa.loc[mapa["alcaldia"].notna()].copy()
    columnas_suma = [
        columna
        for columna in ("No_Guard", "C_No_Guard", "pob_2010")
        if columna in mapa.columns
    ]
    agregados = mapa.dissolve(
        by="alcaldia",
        aggfunc={columna: "sum" for columna in columnas_suma},
    ).reset_index()
    conteos = (
        mapa.groupby("alcaldia", as_index=False)
        .size()
        .rename(columns={"size": "poligonos_infraestructura"})
    )
    agregados = agregados.merge(conteos, on="alcaldia", validate="one_to_one")
    return gpd.GeoDataFrame(agregados, geometry="geometry", crs=mapa.crs)


def _agregar_enut(enut: pd.DataFrame) -> dict[str, float]:
    """Calcula KPIs agregados de cuidado sin territorializarlos."""

    requeridas = {
        "personas_estimadas_que_realizan_cuidado",
        "horas_promedio_semanales_cuidado_entre_cuidadores",
    }
    faltantes = requeridas.difference(enut.columns)
    if faltantes:
        raise ValueError(f"ENUT no contiene columnas requeridas: {sorted(faltantes)}")
    cuidado = pd.to_numeric(
        enut["personas_estimadas_que_realizan_cuidado"], errors="coerce"
    ).fillna(0)
    horas_semanales = pd.to_numeric(
        enut["horas_promedio_semanales_cuidado_entre_cuidadores"],
        errors="coerce",
    )
    if horas_semanales.isna().any():
        raise ValueError(
            "ENUT contiene horas semanales de cuidado no válidas."
        )
    total_cuidadores = cuidado.sum()
    if total_cuidadores <= 0:
        raise ValueError(
            "ENUT no contiene un total positivo de personas cuidadoras."
        )
    horas = (horas_semanales * cuidado).sum() / total_cuidadores
    poblacion = pd.to_numeric(
        enut.get("poblacion_estimada_12_mas", pd.Series(dtype=float)),
        errors="coerce",
    ).fillna(0).sum()
    return {
        "enut_poblacion_12_mas": float(poblacion),
        "enut_personas_que_cuidan": float(total_cuidadores),
        "enut_porcentaje_que_cuida": float(
            total_cuidadores / poblacion * 100
        ) if poblacion > 0 else 0.0,
        "enut_horas_promedio_cuidado": float(horas),
    }


def _validar_indicadores_macro(macro: pd.DataFrame) -> dict[str, str]:
    """Valida y conserva los indicadores macroeconómicos declarados como fuente."""

    requeridas = {"indicador", "valor", "fuente"}
    faltantes = requeridas.difference(macro.columns)
    if faltantes:
        raise ValueError(
            "Indicadores macro no contiene columnas requeridas: "
            f"{sorted(faltantes)}"
        )
    return {
        str(fila["indicador"]): str(fila["valor"])
        for _, fila in macro.iterrows()
        if pd.notna(fila["indicador"])
    }


def _extraer_horas_cuidado_mujeres(macro: pd.DataFrame) -> float:
    """Extrae las horas semanales de cuidado de mujeres de la fuente macro."""

    indicador = "Horas semanales promedio de cuidado (Mujeres)"
    filas = macro.loc[macro["indicador"].eq(indicador), "valor"]
    if filas.empty:
        raise ValueError(
            f"Indicadores macro no contiene el indicador requerido: {indicador}"
        )
    coincidencia = re.search(r"(\d+(?:[.,]\d+)?)", str(filas.iloc[0]))
    if coincidencia is None:
        raise ValueError(
            f"El valor del indicador {indicador} no contiene horas numéricas."
        )
    horas = float(coincidencia.group(1).replace(",", "."))
    if horas <= 0:
        raise ValueError(f"El valor del indicador {indicador} debe ser positivo.")
    return horas


def _poblacion_dependiente(censo: pd.DataFrame) -> pd.Series:
    """Suma la población de 0 a 14 y de 60 años o más del Censo."""

    grupos_edad = [
        "pob_De 0 a 4 años",
        "pob_De 5 a 9 años",
        "pob_De 10 a 14 años",
        "pob_De 60 a 64 años",
        "pob_De 65 a 69 años",
        "pob_De 70 a 74 años",
        "pob_De 75 a 79 años",
        "pob_De 80 a 84 años",
        "pob_85 años y más",
    ]
    faltantes = [columna for columna in grupos_edad if columna not in censo.columns]
    if faltantes:
        raise ValueError(
            "Censo no contiene columnas de población dependiente: "
            + ", ".join(faltantes)
        )
    return censo[grupos_edad].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)


def _estimar_cuidadores_sin_trabajo(enut, territorial, censo):
    """Distribución proporcional exploratoria; no mide abandono ni causalidad."""
    cuidado = pd.to_numeric(enut["personas_estimadas_que_realizan_cuidado"], errors="raise")
    trabajo = pd.to_numeric(enut["personas_estimadas_cuidado_y_trabajo_mercado"], errors="raise")
    if (trabajo > cuidado).any() or cuidado.isna().any() or trabajo.isna().any():
        raise ValueError("Conteos ENUT inconsistentes")
    pesos = _poblacion_dependiente(censo)
    if pesos.sum() <= 0:
        raise ValueError("Población de referencia inválida")
    return territorial["alcaldia"].map(dict(zip(censo["alcaldia"], pesos / pesos.sum()))) * (cuidado - trabajo).sum()


def construir_dataset_consolidado(
    *,
    ruta_observatorio: str | Path = DEFAULT_OBSERVATORIO,
    ruta_censo: str | Path = DEFAULT_CENSO,
    ruta_enut: str | Path = DEFAULT_ENUT,
    ruta_macro: str | Path = DEFAULT_MACRO,
    ruta_shapefile: str | Path = DEFAULT_SHAPEFILE,
) -> gpd.GeoDataFrame:
    """Integra exclusivamente las cinco fuentes de evidencia del proyecto."""

    tablas = cargar_tabulares(
        [ruta_observatorio, ruta_censo, ruta_enut, ruta_macro]
    )
    observatorio = tablas[Path(ruta_observatorio).stem]
    censo = tablas[Path(ruta_censo).stem]
    enut = tablas[Path(ruta_enut).stem]
    macro = tablas[Path(ruta_macro).stem]

    observatorio = observatorio.loc[observatorio["alcaldia"] != "TOTAL CDMX"].copy()
    if censo["alcaldia"].duplicated().any() or observatorio["alcaldia"].duplicated().any():
        raise ValueError("Alcaldías duplicadas: revisar fuentes antes de integrar")
    territorial = observatorio.merge(
        censo,
        on="alcaldia",
        how="outer",
        suffixes=("", "_censo"),
        validate="one_to_one",
    )
    infraestructura = _agregar_infraestructura(cargar_shapefile(ruta_shapefile))
    consolidado = infraestructura.merge(
        territorial,
        on="alcaldia",
        how="outer",
        validate="one_to_one",
    )
    consolidado = gpd.GeoDataFrame(
        consolidado, geometry="geometry", crs=infraestructura.crs
    )
    consolidado["estimacion_cuidadores_sin_trabajo_mercado"] = _estimar_cuidadores_sin_trabajo(
        enut, consolidado, censo
    )

    if "cobertura_caci_0_2_pct" in consolidado:
        consolidado["brecha_cobertura_caci_0_2_pct"] = (
            100 - consolidado["cobertura_caci_0_2_pct"]
        )
    if {"No_Guard", "pob_Total"}.issubset(consolidado.columns):
        consolidado["guarderias_por_1000_habitantes"] = (
            consolidado["No_Guard"] / consolidado["pob_Total"] * 1000
        )
    consolidado = consolidado.sort_values("alcaldia").reset_index(drop=True)
    consolidado.attrs["indicadores_pobreza_tiempo_cdmx"] = _agregar_enut(enut)
    consolidado.attrs["indicadores_pobreza_tiempo_cdmx"][
        "enut_horas_cuidado_mujeres"
    ] = float(enut.loc[enut["sexo_label"].eq("Mujer"), "horas_promedio_semanales_cuidado_entre_cuidadores"].iloc[0])
    consolidado.attrs["fuente_pobreza_tiempo"] = Path(ruta_enut).name
    consolidado.attrs["indicadores_macro_economia_cuidado"] = (
        _validar_indicadores_macro(macro)
    )
    consolidado.attrs["fuentes_evidencia"] = tuple(
        Path(ruta).name
        for ruta in (
            ruta_enut,
            ruta_censo,
            ruta_shapefile,
            ruta_observatorio,
            ruta_macro,
        )
    )
    return consolidado


if __name__ == "__main__":
    dataset = construir_dataset_consolidado()
    print(
        f"Dataset consolidado: {len(dataset)} alcaldías, "
        f"{len(dataset.columns)} columnas, CRS {dataset.crs}"
    )
