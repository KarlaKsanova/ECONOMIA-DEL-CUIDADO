import re
import unicodedata
import json
from pathlib import Path
import geopandas as gpd
import pandas as pd
from cuidado.config import ROOT_DIR

def leer_dataset_preparado():
    path = ROOT_DIR / "data/processed/observatorio.parquet"
    if not path.exists():
        raise FileNotFoundError("Falta el dataset preparado. Ejecuta: python -m cuidado.pipelines.preparar")
    data = gpd.read_parquet(path)
    data.attrs = json.loads(path.with_suffix(".metadata.json").read_text(encoding="utf-8"))
    return data

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


def cargar_evidencia():
    dataset = leer_dataset_preparado()
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
