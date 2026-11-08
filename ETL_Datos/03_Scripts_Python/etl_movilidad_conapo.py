
import pandas as pd
from pathlib import Path

CARPETA_PROYECTO = Path(__file__).resolve().parent.parent

CARPETA_ORIGINALES = (
    CARPETA_PROYECTO / "01_Datos originales"
)

CARPETA_PROCESADOS = (
    CARPETA_PROYECTO / "02_Datos_Procesados"
)



def procesar_conapo():
    """Procesa las proyecciones de CONAPO para 2021-2030."""

    print("\n--- PROCESAMIENTO DE CONAPO ---")

    archivo_origen = (
        CARPETA_ORIGINALES
        / "CONAPO_FILTRADO_CDMX_1990_2040.csv"
    )

    archivo_salida = (
        CARPETA_PROCESADOS
        / "CONAPO_CDMX_PROCESADO_2021_2030.csv"
    )

    if archivo_salida.exists():
        print("El CSV procesado ya existe.")
        print("Se conserva sin modificaciones.")
        return

    df = pd.read_csv(archivo_origen)

    df_procesado = df[
        (df["ANO"] >= 2021)
        & (df["ANO"] <= 2030)
    ].copy()

    print("Registros:", len(df_procesado))
    print("Columnas:", len(df_procesado.columns))
    print("Alcaldías:", df_procesado["NOM_MUN"].nunique())

    duplicados = df_procesado.duplicated(
        subset=["CLAVE", "ANO", "SEXO"]
    ).sum()

    nulos = df_procesado.isna().sum().sum()

    if (
        df_procesado.shape != (320, 27)
        or df_procesado["NOM_MUN"].nunique() != 16
        or duplicados != 0
        or nulos != 0
    ):
        raise ValueError(
            "La base CONAPO no cumple las validaciones."
        )

    df_procesado.to_csv(
        archivo_salida,
        index=False,
        encoding="utf-8-sig"
    )

    print("CONAPO exportado correctamente.")



def procesar_movilidad():
    """Integra rutas y paradas del sistema GTFS."""

    print("\n--- PROCESAMIENTO DE MOVILIDAD ---")

    archivo_salida = (
        CARPETA_PROCESADOS
        / "MOVILIDAD_CDMX_RUTAS_PARADAS.csv"
    )

    if archivo_salida.exists():
        print("El CSV de movilidad ya existe.")
        print("Se conserva sin modificaciones.")
        return

    df_agency = pd.read_csv(
        CARPETA_ORIGINALES / "agency.txt"
    )

    df_routes = pd.read_csv(
        CARPETA_ORIGINALES / "routes.txt"
    )

    df_stops = pd.read_csv(
        CARPETA_ORIGINALES / "stops.txt"
    )

    df_trips = pd.read_csv(
        CARPETA_ORIGINALES / "trips.txt"
    )

    df_stop_times = pd.read_csv(
        CARPETA_ORIGINALES / "stop_times.txt"
    )

    df_movilidad = df_routes.merge(
        df_agency,
        on="agency_id",
        how="left",
        validate="many_to_one"
    )

    df_viajes_rutas = df_trips.merge(
        df_movilidad,
        on="route_id",
        how="left",
        validate="many_to_one"
    )

    df_viajes_paradas = df_stop_times.merge(
        df_viajes_rutas,
        on="trip_id",
        how="left",
        validate="many_to_one"
    )

    df_movilidad_completa = df_viajes_paradas.merge(
        df_stops,
        on="stop_id",
        how="left",
        validate="many_to_one"
    )

    columnas = [
        "route_id",
        "agency_id",
        "agency_name",
        "route_short_name",
        "route_long_name",
        "stop_id",
        "stop_name",
        "stop_lat",
        "stop_lon"
    ]

    df_final = (
        df_movilidad_completa[columnas]
        .drop_duplicates(
            subset=["route_id", "stop_id"]
        )
        .copy()
    )

    print("Relaciones:", len(df_final))
    print("Rutas:", df_final["route_id"].nunique())
    print("Paradas:", df_final["stop_id"].nunique())

    if (
        df_final.shape != (22532, 9)
        or df_final["route_id"].nunique() != 300
        or df_final["stop_id"].nunique() != 10961
        or df_final.isna().sum().sum() != 0
    ):
        raise ValueError(
            "La base de movilidad no cumple las validaciones."
        )

    df_final.to_csv(
        archivo_salida,
        index=False,
        encoding="utf-8-sig"
    )

    print("Movilidad exportada correctamente.")



def procesar_empresas():
    import os
    """Genera empresas sintéticas si el CSV no existe."""
    import subprocess
    import sys

    print("\n--- PROCESAMIENTO DE EMPRESAS B2B2C ---")

    archivo_salida = (
        CARPETA_PROCESADOS / "EMPRESAS_B2B2C_CDMX.csv"
    )

    if archivo_salida.exists():
        print("El CSV de empresas ya existe.")
        print("Se conserva sin modificaciones.")
        return

    archivo_excel = (
        CARPETA_ORIGINALES / "Codigos_Postales_CDMX.xls"
    )

    if not archivo_excel.is_file():
        raise FileNotFoundError(
            f"No se encontró el catálogo: {archivo_excel}"
        )

    ruta_generador = (
        CARPETA_PROYECTO
        / "03_Scripts_Python"
        / "mock_datos_empresas.py"
    )

    if not ruta_generador.is_file():
        raise FileNotFoundError(
            f"No se encontró el generador: {ruta_generador}"
        )

    entorno = os.environ.copy()
    entorno["B2B2C_CARPETA_SALIDA"] = str(CARPETA_PROCESADOS)

    resultado = subprocess.run(
        [sys.executable, "-X", "utf8", str(ruta_generador)],
        input=str(archivo_excel) + "\n",
        cwd=str(ruta_generador.parent),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        env=entorno
    )

    print(resultado.stdout)

    if resultado.returncode != 0:
        raise RuntimeError(
            "Falló el generador B2B2C:\n"
            + resultado.stderr
        )

    if not archivo_salida.is_file():
        raise RuntimeError(
            "El generador terminó sin crear el CSV esperado."
        )

    print("Empresas B2B2C generadas correctamente.")

def main():
    print("ETL de población y movilidad")
    print("Observatorio de Datos - CDMX")

    print("\n--- VERIFICACIÓN DE CARPETAS ---")
    print("Carpeta del proyecto:", CARPETA_PROYECTO.is_dir())
    print("Datos originales:", CARPETA_ORIGINALES.is_dir())
    print("Datos procesados:", CARPETA_PROCESADOS.is_dir())

    procesar_conapo()

    procesar_movilidad()

    procesar_empresas()


if __name__ == "__main__":
    main()
