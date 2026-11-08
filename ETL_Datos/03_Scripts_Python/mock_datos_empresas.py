#!/usr/bin/env python
# coding: utf-8

# In[7]:


# ==================================================
# PROYECTO: OBSERVATORIO DE DATOS
# Economía del Cuidado - Ciudad de México
#
# Módulo: Empresas sintéticas B2B2C
# Archivo: mock_datos_empresas.py
# ==================================================

import pandas as pd
import numpy as np


def main():
    print("Generador de empresas sintéticas B2B2C")
    print("Proyecto Observatorio de Datos - CDMX")

    # Solicitar la ubicación del archivo original
    ruta_archivo = input(
        "\nEscribe la ruta del archivo de códigos postales: "
    ).strip().strip('"')

    # Leer el catálogo oficial
    df_cp = pd.read_excel(
        ruta_archivo,
        sheet_name="Distrito_Federal",
        dtype={"d_codigo": str},
        engine="xlrd"
    )

    print("\nCatálogo cargado correctamente.")
    print("Registros disponibles:", len(df_cp))
    print("Alcaldías:", df_cp["D_mnpio"].nunique())
    print("Códigos postales:", df_cp["d_codigo"].nunique())

    # Seleccionar columnas necesarias
    df_cp_limpio = df_cp[
        ["d_codigo", "d_asenta", "D_mnpio", "d_estado"]
    ].copy()

    # Conservar códigos postales de cinco dígitos
    df_cp_limpio["d_codigo"] = (
        df_cp_limpio["d_codigo"]
        .astype(str)
        .str.zfill(5)
    )

    # Eliminar combinaciones duplicadas
    df_cp_limpio = df_cp_limpio.drop_duplicates(
        subset=["d_codigo", "D_mnpio"]
    )

    # Seleccionar tres códigos por alcaldía
    seleccion_inicial = (
        df_cp_limpio.groupby(
            "D_mnpio",
            group_keys=False
        ).sample(n=3, random_state=42)
    )

    # Identificar códigos todavía no seleccionados
    restantes = df_cp_limpio[
        ~df_cp_limpio.index.isin(seleccion_inicial.index)
    ]

    # Completar hasta llegar a 50
    seleccion_extra = restantes.sample(
        n=50 - len(seleccion_inicial),
        random_state=42
    )

    df_cp_50 = pd.concat(
        [seleccion_inicial, seleccion_extra],
        ignore_index=True
    )

    # Validar resultados
    print("\n--- SELECCIÓN DE CÓDIGOS POSTALES ---")
    print("Códigos seleccionados:", len(df_cp_50))
    print(
        "Alcaldías representadas:",
        df_cp_50["D_mnpio"].nunique()
    )
    print(
        "Códigos distintos:",
        df_cp_50["d_codigo"].nunique()
    )


    # ==========================================
    # GENERACIÓN DE EMPRESAS SINTÉTICAS
    # ==========================================

    df_empresas = df_cp_50.copy().reset_index(drop=True)

    # Generador aleatorio reproducible
    rng = np.random.default_rng(42)

    # Identificadores y nombres ficticios
    df_empresas["empresa_id"] = [
        f"EMP_{i:03d}"
        for i in range(1, len(df_empresas) + 1)
    ]

    df_empresas["nombre_empresa"] = [
        f"Empresa Simulada {i:03d}"
        for i in range(1, len(df_empresas) + 1)
    ]

    # Sectores empresariales
    sectores = [
        "Comercio",
        "Servicios",
        "Tecnología",
        "Manufactura",
        "Logística"
    ]

    df_empresas["sector"] = rng.choice(
        sectores,
        size=len(df_empresas)
    )

    # Cantidad simulada de empleados
    df_empresas["num_empleados"] = rng.integers(
        10, 501,
        size=len(df_empresas)
    )

    # Porcentaje simulado de uso de transporte público
    df_empresas["porcentaje_transporte_publico"] = rng.integers(
        30, 91,
        size=len(df_empresas)
    )

    # Estimación de empleados que usan transporte público
    df_empresas["empleados_transporte_publico"] = (
        df_empresas["num_empleados"]
        * df_empresas["porcentaje_transporte_publico"]
        / 100
    ).round().astype(int)

    # Turnos laborales ficticios
    turnos = ["Matutino", "Vespertino", "Mixto"]

    df_empresas["turno_laboral"] = rng.choice(
        turnos,
        size=len(df_empresas)
    )

    # Interés simulado en soluciones de movilidad
    df_empresas["interes_movilidad"] = rng.choice(
        ["Alto", "Medio", "Bajo"],
        size=len(df_empresas)
    )

    # ==========================================
    # VALIDACIÓN DE RESULTADOS
    # ==========================================

    print("\n--- EMPRESAS SINTÉTICAS ---")
    print("Empresas generadas:", len(df_empresas))
    print(
        "Identificadores únicos:",
        df_empresas["empresa_id"].nunique()
    )
    print(
        "Alcaldías representadas:",
        df_empresas["D_mnpio"].nunique()
    )
    print(
        "Valores faltantes:",
        df_empresas.isna().sum().sum()
    )


    # ==========================================
    # EXPORTACIÓN DE EMPRESAS SINTÉTICAS
    # ==========================================

    from pathlib import Path

    # Carpeta de datos procesados del proyecto
    import os
    carpeta_salida = Path(
        os.environ.get(
            "B2B2C_CARPETA_SALIDA",
            str(Path(__file__).resolve().parent.parent / "02_Datos_Procesados")
        )
    )

    # Crear la carpeta si no existe
    carpeta_salida.mkdir(
        parents=True,
        exist_ok=True
    )

    # Nombre y ubicación del archivo CSV
    archivo_salida = (
        carpeta_salida / "EMPRESAS_B2B2C_CDMX.csv"
    )

    # EXPORTACIÓN SEGURA DE EMPRESAS

    if archivo_salida.exists():
        print("El archivo de empresas ya existe.")
        print("Se conserva sin modificaciones.")
        print("Ubicación:", archivo_salida)
    else:
        df_empresas.to_csv(
            archivo_salida,
            index=False,
            encoding="utf-8-sig"
        )
        print("Archivo exportado correctamente.")
        print("Ubicación:", archivo_salida)





if __name__ == "__main__":
    main()
